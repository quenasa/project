"""
Socioeconomic Data Service
Handles fetching and processing socioeconomic data from WorldPop API
"""
from datetime import datetime
import requests
from flask import current_app


class SocioeconomicService:
    """Service for socioeconomic data operations using WorldPop SDI API"""
    
    def __init__(self):
        """Initialize the socioeconomic service"""
        self.worldpop_url = None
    
    def _init_worldpop(self):
        """Initialize WorldPop API URL"""
        if self.worldpop_url is None:
            self.worldpop_url = current_app.config.get('WORLDPOP_API_URL', 
                                                       'https://www.worldpop.org/sdi/api')
    
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
            # 1. Population density
            population = self.get_population_data(lat, lon, country)
            data["population"] = population
            
            # 2. Poverty indicators
            poverty = self.get_poverty_index(lat, lon, country)
            data["poverty_index"] = poverty
            
            # 3. Access to basic services
            services = self.get_services_access(lat, lon, country)
            data["basic_services_access"] = services
            
            # 4. Income estimates
            income = self.estimate_income_level(lat, lon, country)
            data["average_income"] = income
            
            # 5. Human Development Index (local estimate)
            hdi = self.estimate_local_hdi(lat, lon, country)
            data["human_development_index"] = hdi
            
        except Exception as e:
            print(f"Error fetching socioeconomic data: {e}")
            data["error"] = str(e)
        
        return data
    
    def get_population_data(self, lat, lon, country=None):
        """
        Get population density and demographics from WorldPop
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country code
            
        Returns:
            dict: Population data
        """
        try:
            self._init_worldpop()
            
            today = datetime.now()
            current_year = today.year
            
            # WorldPop REST API provides GeoTIFF files, not point queries
            # To implement: Download country GeoTIFF, extract point value
            # API: https://www.worldpop.org/rest/data/pop/wpgp
            # 
            # For production:
            # 1. Use WOPR API if available for country: https://wopr.worldpop.org/
            # 2. Or integrate with local census data
            # 3. Or download and cache GeoTIFF files per country
            
            return {
                "total": 0,
                "density_per_km2": 0.0,
                "growth_rate": 0.0,
                "year": current_year,
                "age_distribution": {
                    "0-14": 0,
                    "15-64": 0,
                    "65+": 0
                },
                "source": "WorldPop (requires GeoTIFF download)",
                "note": "WorldPop API provides raster files, not point queries. Requires downloading country data."
            }
            
        except Exception as e:
            return {
                "total": 0,
                "density_per_km2": 0.0,
                "error": str(e)
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
                    "index": 0.0,
                    "percentage_below_poverty_line": 0.0,
                    "gini_coefficient": 0.0,
                    "source": "World Bank",
                    "note": "Country name required"
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
            
            poverty_rate = 0.0
            gini = 0.0
            poverty_year = None
            gini_year = None
            
            # Get poverty rate
            response = requests.get(poverty_url, params=params, timeout=10)
            if response.ok:
                data = response.json()
                if len(data) > 1 and data[1]:
                    for entry in data[1]:
                        if entry.get('value'):
                            poverty_rate = round(entry['value'], 2)
                            poverty_year = entry['date']
                            break
            
            # Get Gini coefficient
            response = requests.get(gini_url, params=params, timeout=10)
            if response.ok:
                data = response.json()
                if len(data) > 1 and data[1]:
                    for entry in data[1]:
                        if entry.get('value'):
                            gini = round(entry['value'], 2)
                            gini_year = entry['date']
                            break
            
            if poverty_rate > 0 or gini > 0:
                print(f"[INFO] ✅ Poverty data: {poverty_rate}% below poverty line, Gini: {gini}")
                
                # Calculate composite poverty index (0-100)
                poverty_index = round((poverty_rate + gini) / 2, 2) if poverty_rate and gini else poverty_rate
                
                return {
                    "index": poverty_index,
                    "percentage_below_poverty_line": poverty_rate,
                    "gini_coefficient": gini,
                    "source": "World Bank",
                    "poverty_year": poverty_year,
                    "gini_year": gini_year,
                    "status": "success"
                }
            
            return {
                "index": 0.0,
                "percentage_below_poverty_line": 0.0,
                "gini_coefficient": 0.0,
                "source": "World Bank",
                "note": f"No poverty data available for {country}"
            }
            
        except Exception as e:
            return {"index": 0.0, "error": str(e)}
    
    def get_services_access(self, lat, lon, country=None):
        """
        Get access to basic services (water, health, education)
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            country (str, optional): Country code
            
        Returns:
            dict: Services access indicators (0-100%)
        """
        try:
            # Requires:
            # 1. DHS (Demographic and Health Surveys): https://dhsprogram.com/data/
            # 2. WorldPop accessibility datasets (travel time to facilities)
            # 3. Or national statistics bureaus
            # 4. WHO/UNICEF Joint Monitoring Programme for Water Supply
            
            return {
                "water": 0.0,      # % with access to clean water
                "health": 0.0,     # % with access to health facilities
                "education": 0.0,  # % with access to schools
                "electricity": 0.0,
                "sanitation": 0.0,
                "source": "DHS / National statistics not integrated",
                "note": "Requires DHS API or national statistics bureau data"
            }
            
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
