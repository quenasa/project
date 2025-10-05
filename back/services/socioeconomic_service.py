"""
Socioeconomic Data Service
Handles fetching and processing socioeconomic data from WorldPop API
"""
from datetime import datetime
import requests
import tempfile
import os
from flask import current_app

try:
    import rasterio
    from rasterio.transform import rowcol
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    print("[WARNING] rasterio not installed. Install with: pip install rasterio")


class SocioeconomicService:
    """Service for socioeconomic data operations using WorldPop SDI API"""
    
    def __init__(self):
        """Initialize the socioeconomic service"""
        self.worldpop_url = None
        
        # Quality ranges for socioeconomic indicators (0-100 for percentages/indices)
        self.quality_ranges = {
            'poverty': (0, 100),
            'gini': (0, 100), 
            'unemployment': (0, 100),
            'school_enrollment': (0, 100),
            'water_withdrawal': (0, 100),
            'received_wages': (0, 100),
            'health_coverage': (0, 100)
        }
    
    def _pack(self, indicator, value, unit, year=None, period=None, source="",
              method="national statistic", status="success", note=None):
        """Pack socioeconomic data with unified structure and quality checks"""
        
        # Quality range check
        quality_check = "unknown"
        if value is not None and indicator in self.quality_ranges:
            min_val, max_val = self.quality_ranges[indicator]
            if min_val <= value <= max_val:
                quality_check = "pass"
            else:
                quality_check = "fail"
        elif value is None:
            quality_check = "no_data"
        
        # Format unit properly to avoid concatenation issues with None
        display_unit = unit if value is not None else ""
        
        result = {
            'indicator': indicator,
            'value': value,
            'unit': display_unit,
            'source': source,
            'method': method,
            'status': status,
            'quality': {
                'range_check': quality_check
            }
        }
        
        # Add temporal info
        if year:
            result['year'] = year
        if period:
            result['period'] = period
            
        # Add note if provided
        if note:
            result['note'] = note
            
        return result
    
    def _init_worldpop(self):
        """Initialize WorldPop API URL"""
        if self.worldpop_url is None:
            self.worldpop_url = current_app.config.get('WORLDPOP_API_URL', 
                                                       'https://www.worldpop.org/sdi/api')
    
    def get_country_socioeconomic_data(self, iso3_code, country_name):
        """
        Obtener datos socioeconómicos agregados para un país completo
        Optimizado para datos a nivel país (más rápido que por coordenadas)
        
        Args:
            iso3_code (str): Código ISO3 del país (ej: NGA, KEN)
            country_name (str): Nombre del país
            
        Returns:
            dict: Indicadores socioeconómicos a nivel país
        """
        data = {
            "country": country_name,
            "iso3": iso3_code,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # DEMOGRAPHICS
            # 1. Population density (World Bank - agregado nacional)
            population = self.get_country_population(iso3_code, country_name)
            data["population"] = population
            
            # 2. Poverty rate (World Bank)
            poverty = self.get_poverty_index(None, None, country_name)
            data["poverty_index"] = poverty
            
            # SOCIOECONOMICS
            # 3. Water withdrawal (World Bank)
            water_use = self.get_water_withdrawal(None, None, country_name)
            data["water_withdrawal"] = water_use
            
            # 4. School enrollment % net (World Bank)
            school = self.get_school_enrollment(None, None, country_name)
            data["school_enrollment"] = school
            
            # 5. Unemployment rate (World Bank)
            unemployment = self.get_unemployment_rate(None, None, country_name)
            data["unemployment"] = unemployment
            
            # 6. Received wages (World Bank)
            wages = self.get_received_wages(None, None, country_name)
            data["received_wages"] = wages
            
            # 7. Health-Service Coverage Index (World Bank)
            health = self.get_health_coverage_index(None, None, country_name)
            data["health_coverage"] = health
            
        except Exception as e:
            print(f"Error fetching country socioeconomic data: {e}")
            data["error"] = str(e)
        
        return data
    
    def get_country_population(self, iso3_code, country_name):
        """
        Obtener densidad poblacional a nivel país (World Bank)
        Mucho más rápido que GeoTIFF de WorldPop
        
        Args:
            iso3_code (str): Código ISO3 del país
            country_name (str): Nombre del país
            
        Returns:
            dict: Densidad poblacional del país
        """
        try:
            # World Bank: Population density (people per sq. km of land area)
            url = f"https://api.worldbank.org/v2/country/{iso3_code}/indicator/EN.POP.DNST"
            params = {"format": "json", "date": "2015:2023", "per_page": 20}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.ok:
                data = response.json()
                if len(data) > 1 and data[1]:
                    for entry in data[1]:
                        if entry.get('value'):
                            density = round(entry['value'], 1)
                            year = entry['date']
                            
                            print(f"[INFO] ✅ Population density: {density} people/km² ({year})")
                            
                            return self._pack(
                                indicator='population',
                                value=density,
                                unit=' people/km²',
                                year=year,
                                source='World Bank (EN.POP.DNST)',
                                status='success'
                            )
            
            return self._pack(
                indicator='population',
                value=None,
                unit=' people/km²',
                source='World Bank (EN.POP.DNST)',
                status='no_data'
            )
            
        except Exception as e:
            print(f"[ERROR] Population density retrieval failed: {e}")
            return self._pack(
                indicator='population',
                value=None,
                unit=' people/km²',
                source='World Bank (EN.POP.DNST)',
                status='error',
                note=str(e)
            )
    
    def get_socioeconomic_data(self, lat, lon, location_name=None, country=None):
        """
        Get socioeconomic data for a location in Africa
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            location_name (str, optional): Name of the location
            country (str, optional): Country name
            
        Returns:
            dict: Socioeconomic indicators
        """
        self._init_worldpop()
        
        data = {
            "location": {
                "lat": lat,
                "lon": lon,
                "name": location_name or f"Location ({lat}, {lon})",
                "country": country or "Unknown"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # DEMOGRAPHICS
            # 1. Population density (WorldPop)
            population = self.get_population_data(lat, lon, country)
            data["population"] = population
            
            # 2. Poverty rate (WorldPop or World Bank)
            poverty = self.get_poverty_index(lat, lon, country)
            data["poverty_index"] = poverty
            
            # SOCIOECONOMICS
            # 3. Water withdrawal (World Bank FAO_AS_4261)
            water_use = self.get_water_withdrawal(lat, lon, country)
            data["water_withdrawal"] = water_use
            
            # 4. School enrollment % net (World Bank WB_HNP_SE_NENR)
            school = self.get_school_enrollment(lat, lon, country)
            data["school_enrollment"] = school
            
            # 5. Unemployment rate (World Bank WB_GS_SL_UEM_ZS)
            unemployment = self.get_unemployment_rate(lat, lon, country)
            data["unemployment"] = unemployment
            
            # 6. Received wages (World Bank WB_FINDEX_FIN32)
            wages = self.get_received_wages(lat, lon, country)
            data["received_wages"] = wages
            
            # 7. Health-Service Coverage Index (World Bank UHC)
            health = self.get_health_coverage_index(lat, lon, country)
            data["health_coverage"] = health
            
        except Exception as e:
            print(f"Error fetching socioeconomic data: {e}")
            data["error"] = str(e)
        
        return data
    
    def get_population_data(self, lat, lon, country=None):
        """
        Get population density from WorldPop GeoTIFF data
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country name
            
        Returns:
            dict: Population density data
        """
        try:
            if not RASTERIO_AVAILABLE:
                return {
                    "density_per_km2": 0.0,
                    "source": "WorldPop",
                    "status": "not_configured",
                    "note": "rasterio library required - pip install rasterio"
                }
            
            if not country:
                return {
                    "density_per_km2": 0.0,
                    "source": "WorldPop",
                    "note": "Country name required"
                }
            
            # ISO3 country code mapping
            iso3_map = {
                "Nigeria": "NGA", "Kenya": "KEN", "South Africa": "ZAF", "Egypt": "EGY",
                "Ethiopia": "ETH", "Ghana": "GHA", "Morocco": "MAR", "Algeria": "DZA",
                "Tanzania": "TZA", "Uganda": "UGA", "Senegal": "SEN", "Rwanda": "RWA"
            }
            
            iso3 = iso3_map.get(country, country.upper()[:3])
            current_year = datetime.now().year
            
            # Try years from current back to 2020
            for year in range(current_year, 2019, -1):
                try:
                    # WorldPop constrained population dataset (100m resolution)
                    # URL format: https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/BSGM/{ISO3}/{iso3}_ppp_{year}_UNadj_constrained.tif
                    
                    url = f"https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/{year}/BSGM/{iso3}/{iso3.lower()}_ppp_{year}_UNadj_constrained.tif"
                    
                    print(f"[INFO] Downloading WorldPop GeoTIFF for {country} ({year})...")
                    
                    # Download GeoTIFF to temp file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tif')
                    temp_path = temp_file.name
                    temp_file.close()
                    
                    response = requests.get(url, timeout=30, stream=True)
                    
                    if not response.ok:
                        print(f"[INFO] Year {year} not available, trying older...")
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                        continue
                    
                    # Write to temp file
                    with open(temp_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    file_size = os.path.getsize(temp_path)
                    print(f"[INFO] GeoTIFF downloaded: {file_size / (1024*1024):.1f} MB")
                    
                    # Open with rasterio
                    with rasterio.open(temp_path) as src:
                        # Get pixel value at coordinates
                        # rasterio uses (x, y) = (lon, lat) order
                        row, col = rowcol(src.transform, lon, lat)
                        
                        # Check if coordinates are within bounds
                        if 0 <= row < src.height and 0 <= col < src.width:
                            # Read the population value
                            population_value = src.read(1)[row, col]
                            
                            # WorldPop values are population count per pixel
                            # Pixel size is ~100m x 100m = 0.01 km²
                            # Calculate density per km²
                            pixel_area_km2 = 0.01  # 100m x 100m
                            density = float(population_value) / pixel_area_km2
                            
                            # Clean up temp file
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                            
                            print(f"[INFO] ✅ Population density: {density:.1f} people/km² ({year})")
                            
                            return {
                                "density_per_km2": round(density, 1),
                                "year": year,
                                "source": "WorldPop Constrained Population Dataset",
                                "resolution": "100m",
                                "status": "success"
                            }
                        else:
                            print(f"[WARNING] Coordinates outside raster bounds")
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                            continue
                    
                except Exception as e:
                    print(f"[INFO] Error with year {year}: {e}")
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    continue
            
            # If we get here, no data was found
            return {
                "density_per_km2": 0.0,
                "source": "WorldPop",
                "note": f"No population data available for {country}",
                "status": "no_data"
            }
            
        except Exception as e:
            print(f"[ERROR] Population retrieval failed: {e}")
            return {
                "density_per_km2": 0.0,
                "error": str(e),
                "status": "error"
            }
    
    def get_poverty_index(self, lat, lon, country=None):
        """
        Get poverty data from World Bank API
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country name
            
        Returns:
            dict: Poverty indicators
        """
        try:
            if not country:
                return {
                    "index": None,
                    "percentage_below_poverty_line": None,
                    "gini_coefficient": None,
                    "source": "World Bank",
                    "note": "Country name required",
                    "status": "error"
                }
            
            # Get country ISO3 code
            iso3_map = {
                "Nigeria": "NGA", "Kenya": "KEN", "South Africa": "ZAF", "Egypt": "EGY",
                "Ethiopia": "ETH", "Ghana": "GHA", "Morocco": "MAR", "Algeria": "DZA",
                "Tanzania": "TZA", "Uganda": "UGA", "Senegal": "SEN", "Rwanda": "RWA"
            }
            
            iso3 = iso3_map.get(country, country.upper()[:3])
            
            print(f"[INFO] Fetching poverty data from World Bank for {country}...")
            
            # Poverty headcount ratio at $2.15 a day (2017 PPP)
            poverty_url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/SI.POV.DDAY"
            gini_url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/SI.POV.GINI"
            
            params = {
                "format": "json",
                "date": "2010:2023",
                "per_page": 20
            }
            
            poverty_rate = None
            gini = None
            poverty_year = None
            gini_year = None
            
            # Get poverty rate
            response = requests.get(poverty_url, params=params, timeout=10)
            if response.ok:
                data = response.json()
                if len(data) > 1 and data[1]:
                    for entry in data[1]:
                        if entry.get('value') is not None:  # Accept 0.0 as valid
                            poverty_rate = round(entry['value'], 2)
                            poverty_year = entry['date']
                            break
            
            # Get Gini coefficient
            response = requests.get(gini_url, params=params, timeout=10)
            if response.ok:
                data = response.json()
                if len(data) > 1 and data[1]:
                    for entry in data[1]:
                        if entry.get('value') is not None:
                            gini = round(entry['value'], 2)
                            gini_year = entry['date']
                            break
            
            # Calculate composite poverty index with available components only
            comps = [v for v in [poverty_rate, gini] if v is not None]
            if comps:
                poverty_index = round(sum(comps) / len(comps), 2)
                poverty_display = f"{poverty_rate}%" if poverty_rate is not None else "N/A"
                gini_display = f"{gini}" if gini is not None else "N/A"
                print(f"[INFO] Poverty data: {poverty_display} below poverty line, Gini: {gini_display}")
                
                return self._pack(
                    indicator='poverty',
                    value=poverty_index,
                    unit='%',
                    year=poverty_year or gini_year,
                    source='World Bank (SI.POV.DDAY, SI.POV.GINI)',
                    status='success',
                    note=f"Poverty: {poverty_year or 'N/A'}, Gini: {gini_year or 'N/A'}"
                )
            
            print(f"[WARNING] No poverty data available for {country}")
            return self._pack(
                indicator='poverty',
                value=None,
                unit='%',
                source='World Bank (SI.POV.DDAY, SI.POV.GINI)',
                status='no_data',
                note=f"No poverty data available for {country}"
            )
            
        except Exception as e:
            return {"index": None, "error": str(e), "status": "error"}
    
    def get_services_access(self, lat, lon, country=None):
        """
        Get access to basic services using World Bank indicators
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country name
            
        Returns:
            dict: Services access indicators
        """
        try:
            if not country:
                return {
                    "water": 0.0,
                    "health": 0.0,
                    "education": 0.0,
                    "electricity": 0.0,
                    "sanitation": 0.0,
                    "source": "World Bank",
                    "note": "Country name required"
                }
            
            iso3_map = {
                "Nigeria": "NGA", "Kenya": "KEN", "South Africa": "ZAF", "Egypt": "EGY",
                "Ethiopia": "ETH", "Ghana": "GHA", "Morocco": "MAR", "Algeria": "DZA",
                "Tanzania": "TZA", "Uganda": "UGA", "Senegal": "SEN", "Rwanda": "RWA"
            }
            
            iso3 = iso3_map.get(country, country.upper()[:3])
            
            # School enrollment (% net)
            school_url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/SE.PRM.NENR"
            # Access to electricity (% of population)
            elec_url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/EG.ELC.ACCS.ZS"
            # Improved water source (% of population)
            water_url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/SH.H2O.BASW.ZS"
            # Improved sanitation (% of population)
            sanit_url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/SH.STA.BASS.ZS"
            
            params = {"format": "json", "date": "2015:2023", "per_page": 20}
            
            results = {
                "education": 0.0,
                "electricity": 0.0,
                "water": 0.0,
                "sanitation": 0.0,
                "health": 0.0,  # No hay API directa, se deja en 0
                "source": "World Bank"
            }
            
            # Get school enrollment
            try:
                resp = requests.get(school_url, params=params, timeout=10)
                if resp.ok:
                    data = resp.json()
                    if len(data) > 1 and data[1]:
                        for entry in data[1]:
                            if entry.get('value'):
                                results["education"] = round(entry['value'], 1)
                                results["education_year"] = entry['date']
                                break
            except:
                pass
            
            # Get electricity access
            try:
                resp = requests.get(elec_url, params=params, timeout=10)
                if resp.ok:
                    data = resp.json()
                    if len(data) > 1 and data[1]:
                        for entry in data[1]:
                            if entry.get('value'):
                                results["electricity"] = round(entry['value'], 1)
                                results["electricity_year"] = entry['date']
                                break
            except:
                pass
            
            # Get water access
            try:
                resp = requests.get(water_url, params=params, timeout=10)
                if resp.ok:
                    data = resp.json()
                    if len(data) > 1 and data[1]:
                        for entry in data[1]:
                            if entry.get('value'):
                                results["water"] = round(entry['value'], 1)
                                results["water_year"] = entry['date']
                                break
            except:
                pass
            
            # Get sanitation access
            try:
                resp = requests.get(sanit_url, params=params, timeout=10)
                if resp.ok:
                    data = resp.json()
                    if len(data) > 1 and data[1]:
                        for entry in data[1]:
                            if entry.get('value'):
                                results["sanitation"] = round(entry['value'], 1)
                                results["sanitation_year"] = entry['date']
                                break
            except:
                pass
            
            if any(results[k] > 0 for k in ["education", "electricity", "water", "sanitation"]):
                results["status"] = "success"
                print(f"[INFO] ✅ Services access: Education={results['education']}%, Electricity={results['electricity']}%, Water={results['water']}%")
            
            return results
            
        except Exception as e:
            return {
                "water": 0.0,
                "health": 0.0,
                "education": 0.0,
                "error": str(e)
            }
    
    def estimate_income_level(self, lat, lon, country=None):
        """
        Estimate average income level using World Bank GDP data
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country name
            
        Returns:
            dict: Income estimates
        """
        try:
            if not country:
                return {
                    "average_annual_usd": 0.0,
                    "median_annual_usd": 0.0,
                    "economic_activity_level": "unknown",
                    "source": "World Bank",
                    "note": "Country name required for GDP data"
                }
            
            # Get country ISO3 code
            iso3_map = {
                "Nigeria": "NGA", "Kenya": "KEN", "South Africa": "ZAF", "Egypt": "EGY",
                "Ethiopia": "ETH", "Ghana": "GHA", "Morocco": "MAR", "Algeria": "DZA",
                "Tanzania": "TZA", "Uganda": "UGA", "Senegal": "SEN", "Rwanda": "RWA"
            }
            
            iso3 = iso3_map.get(country)
            if not iso3:
                # Try to use country as-is if it's already ISO3
                iso3 = country.upper()[:3]
            
            print(f"[INFO] Fetching GDP data from World Bank for {country} ({iso3})...")
            
            # World Bank API - GDP per capita (current US$)
            url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/NY.GDP.PCAP.CD"
            params = {
                "format": "json",
                "date": "2022:2023",  # Get latest 2 years
                "per_page": 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.ok:
                data = response.json()
                
                if len(data) > 1 and data[1]:
                    # Get most recent value
                    for entry in data[1]:
                        if entry.get('value'):
                            gdp_per_capita = round(entry['value'], 2)
                            year = entry['date']
                            
                            # Classify economic activity
                            if gdp_per_capita < 2000:
                                level = "low"
                            elif gdp_per_capita < 8000:
                                level = "medium"
                            else:
                                level = "high"
                            
                            print(f"[INFO] ✅ GDP per capita: ${gdp_per_capita} ({year})")
                            
                            return {
                                "average_annual_usd": gdp_per_capita,
                                "median_annual_usd": gdp_per_capita * 0.8,  # Rough estimate
                                "economic_activity_level": level,
                                "source": "World Bank",
                                "year": year,
                                "status": "success"
                            }
            
            print(f"[INFO] No GDP data found for {country}")
            return {
                "average_annual_usd": 0.0,
                "median_annual_usd": 0.0,
                "economic_activity_level": "unknown",
                "source": "World Bank",
                "note": f"No GDP data available for {country}"
            }
            
        except Exception as e:
            return {"average_annual_usd": 0.0, "error": str(e)}
    
    def estimate_local_hdi(self, lat, lon, country=None):
        """
        Estimate local Human Development Index
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country code
            
        Returns:
            dict: HDI estimate and components
        """
        try:
            # HDI combines:
            # 1. Life expectancy (health) - WHO or national health data
            # 2. Education level - UNESCO or DHS data
            # 3. Income per capita - World Bank data
            # 
            # UNDP provides country-level HDI: http://hdr.undp.org/en/data
            # For sub-national, need to combine local health, education, income data
            
            return {
                "index": 0.0,  # 0-1
                "components": {
                    "health": 0.0,
                    "education": 0.0,
                    "income": 0.0
                },
                "classification": "unknown",  # low, medium, high, very high
                "source": "UNDP / WHO / UNESCO data not integrated",
                "note": "Requires UNDP HDI data, WHO health data, UNESCO education data"
            }
            
        except Exception as e:
            return {"index": 0.0, "error": str(e)}
    
    def get_worldpop_data(self, dataset, lat, lon, country=None):
        """
        Generic method to query WorldPop API
        
        Args:
            dataset (str): Dataset name
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country code
            
        Returns:
            dict: Dataset response
        """
        try:
            self._init_worldpop()
            
            # Construct API request
            # Example: /v1/wopr/pointtotal?iso3=NGA&lat=6.5244&lon=3.3792
            
            params = {
                'lat': lat,
                'lon': lon
            }
            
            if country:
                # WorldPop uses ISO3 country codes
                params['iso3'] = self._get_iso3_code(country)
            
            # TODO: Make actual HTTP request
            # response = requests.get(f"{self.worldpop_url}/{dataset}", params=params)
            # return response.json()
            
            return {
                "status": "not_implemented",
                "note": "Implement actual HTTP request to WorldPop API"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_iso3_code(self, country_name):
        """
        Convert country name to ISO3 code for WorldPop API
        
        Args:
            country_name (str): Country name
            
        Returns:
            str: ISO3 code
        """
        # Simple mapping for African countries
        country_codes = {
            'nigeria': 'NGA',
            'kenya': 'KEN',
            'south africa': 'ZAF',
            'ethiopia': 'ETH',
            'egypt': 'EGY',
            'tanzania': 'TZA',
            'uganda': 'UGA',
            'ghana': 'GHA',
            'morocco': 'MAR',
            'mozambique': 'MOZ',
            # Add more as needed
        }
        
        return country_codes.get(country_name.lower(), country_name.upper()[:3])
    
    def get_unemployment_rate(self, lat, lon, country=None):
        """
        Get unemployment rate from World Bank
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country name
            
        Returns:
            dict: Unemployment data
        """
        try:
            if not country:
                return {"unemployment_rate": 0.0, "source": "World Bank", "note": "Country name required"}
            
            iso3 = self._get_iso3_code(country)
            
            # Unemployment, total (% of total labor force)
            url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/SL.UEM.TOTL.ZS"
            params = {"format": "json", "date": "2015:2023", "per_page": 20}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.ok:
                data = response.json()
                if len(data) > 1 and data[1]:
                    for entry in data[1]:
                        if entry.get('value') is not None:
                            rate = round(entry['value'], 1)
                            year = entry['date']
                            print(f"[INFO] Unemployment rate: {rate}% ({year})")
                            return self._pack(
                                indicator='unemployment',
                                value=rate,
                                unit='%',
                                year=year,
                                source='World Bank (SL.UEM.TOTL.ZS)',
                                status='success'
                            )
            
            print(f"[WARNING] No unemployment data for {country}")
            return self._pack(
                indicator='unemployment',
                value=None,
                unit='%',
                source='World Bank (SL.UEM.TOTL.ZS)',
                status='no_data',
                note=f"No unemployment data for {country}"
            )
        
        except Exception as e:
            return {"unemployment_rate": None, "error": str(e), "status": "error"}
    
    def get_water_withdrawal(self, lat, lon, country=None):
        """
        Get water withdrawal data from World Bank
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country name
            
        Returns:
            dict: Water withdrawal data
        """
        try:
            if not country:
                return {"water_withdrawal": None, "source": "World Bank", "note": "Country name required", "status": "error"}
            
            iso3 = self._get_iso3_code(country)
            
            # Annual freshwater withdrawals (% of internal resources)
            url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/ER.H2O.FWTL.ZS"
            params = {"format": "json", "date": "2000:2023", "per_page": 30}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.ok:
                data = response.json()
                if len(data) > 1 and data[1]:
                    for entry in data[1]:
                        if entry.get('value') is not None:
                            withdrawal_pct = round(entry['value'], 2)
                            year = entry['date']
                            print(f"[INFO] Water withdrawal: {withdrawal_pct}% of internal resources ({year})")
                            return self._pack(
                                indicator='water_withdrawal',
                                value=withdrawal_pct,
                                unit='%',
                                year=year,
                                source='World Bank (ER.H2O.FWTL.ZS)',
                                status='success'
                            )
            
            print(f"[WARNING] No water withdrawal data for {country}")
            return self._pack(
                indicator='water_withdrawal',
                value=None,
                unit='%',
                source='World Bank (ER.H2O.FWTL.ZS)',
                status='no_data',
                note=f"No water data for {country}"
            )
        
        except Exception as e:
            return {"withdrawal_percentage": 0.0, "error": str(e)}
    
    def get_health_coverage_index(self, lat, lon, country=None):
        """
        Get health service coverage index from World Bank
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country name
            
        Returns:
            dict: Health coverage data
        """
        try:
            if not country:
                return {"health_coverage_index": None, "source": "World Bank", "note": "Country name required", "status": "error"}
            
            iso3 = self._get_iso3_code(country)
            
            # UHC service coverage index
            url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/SH.UHC.SRVS.CV.XD"
            params = {"format": "json", "date": "2015:2023", "per_page": 20}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.ok:
                data = response.json()
                if len(data) > 1 and data[1]:
                    for entry in data[1]:
                        if entry.get('value') is not None:
                            index = round(entry['value'], 1)
                            year = entry['date']
                            print(f"[INFO] Health coverage: {index} index ({year})")
                            return self._pack(
                                indicator='health_coverage',
                                value=index,
                                unit=' index',  # Space before 'index' for better formatting
                                year=year,
                                source='World Bank (SH.UHC.SRVS.CV.XD)',
                                status='success'
                            )
            
            print(f"[WARNING] No health coverage data for {country}")
            return self._pack(
                indicator='health_coverage',
                value=None,
                unit=' index',  # Will be empty due to _pack formatting, but consistent
                source='World Bank (SH.UHC.SRVS.CV.XD)',
                status='no_data',
                note=f"No health coverage data for {country}"
            )
        
        except Exception as e:
            return {"health_coverage_index": None, "error": str(e), "status": "error"}
    
    def get_school_enrollment(self, lat, lon, country=None):
        """
        Get school enrollment rate (% net) from World Bank
        Indicator: WB_HNP_SE_NENR (Children out of school, primary, % of primary school age)
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country name
            
        Returns:
            dict: School enrollment data
        """
        try:
            if not country:
                print(f"[WARNING] School enrollment: No country provided")
                return {"enrollment_rate": None, "source": "World Bank", "note": "Country name required", "status": "error"}
            
            iso3 = self._get_iso3_code(country)
            print(f"[INFO] Requesting school enrollment for {country} ({iso3})")
            
            # Net Enrollment Rate, primary (% of primary school age children)
            url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/SE.PRM.NENR"
            params = {"format": "json", "per_page": 100}
            
            response = requests.get(url, params=params, timeout=10)
            print(f"[INFO] School enrollment response status: {response.status_code}")
            
            if response.ok:
                data = response.json()
                print(f"[INFO] School enrollment response length: {len(data)}")
                if len(data) > 1 and data[1]:
                    print(f"[INFO] School enrollment data entries: {len(data[1])}")
                    for entry in data[1]:
                        value = entry.get('value')
                        if value is not None:
                            enrollment_rate = round(value, 2)  # NENR is already enrollment rate - use directly
                            year = entry['date']
                            print(f"[INFO] School enrollment: {enrollment_rate}% net ({year})")
                            return self._pack(
                                indicator='school_enrollment',
                                value=enrollment_rate,
                                unit='%',
                                year=year,
                                source='World Bank (SE.PRM.NENR)',
                                status='success'
                            )
                    print(f"[WARNING] All school enrollment entries have None values")
            
            print(f"[WARNING] No school enrollment data for {country}")
            return self._pack(
                indicator='school_enrollment',
                value=None,
                unit='%',
                source='World Bank (SE.PRM.NENR)',
                status='no_data',
                note=f"No enrollment data for {country}"
            )
        
        except Exception as e:
            print(f"[ERROR] School enrollment error: {e}")
            return {"enrollment_rate": 0.0, "error": str(e)}
    
    def get_received_wages(self, lat, lon, country=None):
        """
        Get received wages data from World Bank
        Indicator: WB_FINDEX_FIN32 (Received wage payments into a financial institution account, % age 15+)
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country name
            
        Returns:
            dict: Received wages data
        """
        try:
            if not country:
                return {"received_wages_pct": None, "source": "World Bank", "note": "Country name required", "status": "error"}
            
            iso3 = self._get_iso3_code(country)
            
            # Received wage payments into a financial institution account (% age 15+)
            # Indicator: GFDD.AI.11 from Global Financial Development Database
            url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/GFDD.AI.11"
            params = {"format": "json", "date": "2011:2024", "per_page": 30}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.ok:
                data = response.json()
                if len(data) > 1 and data[1]:
                    for entry in data[1]:
                        if entry.get('value') is not None:
                            wages_pct = round(entry['value'], 2)
                            year = entry['date']
                            print(f"[INFO] Received wages: {wages_pct}% ({year})")
                            return self._pack(
                                indicator='received_wages',
                                value=wages_pct,
                                unit='%',
                                year=year,
                                source='World Bank (GFDD.AI.11)',
                                status='success'
                            )
            
            print(f"[WARNING] No received wages data for {country}")
            return self._pack(
                indicator='received_wages',
                value=None,
                unit='%',
                source='World Bank (GFDD.AI.11)',
                status='no_data',
                note=f"No wages data for {country}"
            )
        
        except Exception as e:
            return {"received_wages_pct": None, "error": str(e), "status": "error"}
