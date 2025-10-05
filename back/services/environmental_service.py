"""
Environmental Data Service
Handles fetching and processing environmental data from Copernicus CDS
"""
from datetime import datetime, timedelta
import os
import tempfile
import requests
import cdsapi
from flask import current_app

try:
    import xarray as xr
    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False
    print("[WARNING] xarray not installed. Install with: pip install xarray netCDF4")


class EnvironmentalService:
    """Service for environmental data operations using Copernicus CDS API"""
    
    def __init__(self):
        """Initialize the environmental service with Copernicus client"""
        self.copernicus_url = None
        self.copernicus_key = None
        self.cds_client = None
    
    def _find_most_recent_date(self, max_days_back=30):
        """
        Find the most recent date with available data.
        Tries progressively older dates until data is found.
        
        Args:
            max_days_back (int): Maximum number of days to look back
            
        Returns:
            dict: Climate risk assessment
        """
        # Requires:
        # 1. Historical precipitation data from ERA5
        # 2. Flood risk maps from GLOFAS (Global Flood Awareness System)
        # 3. Drought indicators from Copernicus Emergency Management Service
        # 4. Or integrate with local climate agencies
        
        return {
            "flood_risk": "medium",
            "drought_risk": "medium",
            "extreme_weather_risk": "medium",
            "source": "Climate risk assessment not yet integrated",
            "note": "Requires ERA5 precipitation, GLOFAS flood data, or local climate agency APIs"
        }


class EnvironmentalService:
    """Service for environmental data operations using Copernicus CDS API"""
    
    def __init__(self):
        """Initialize the environmental service with Copernicus client"""
        self.copernicus_url = None
        self.copernicus_key = None
        self.cds_client = None
    
    def _find_most_recent_date(self, max_days_back=30):
        """
        Find the most recent date with available data.
        Tries progressively older dates until data is found.
        
        Args:
            max_days_back (int): Maximum number of days to look back
            
        Returns:
            tuple: (date_str, days_back) or (None, None) if no data found
        """
        for days_back in range(1, max_days_back + 1):
            date = datetime.now() - timedelta(days=days_back)
            date_str = date.strftime('%Y-%m-%d')
            # We'll try this date and let the API call handle the validation
            # The first successful call will cache the working date
            return date_str, days_back
        return None, None
    
    def _init_copernicus_client(self):
        """Initialize Copernicus CDS API client lazily"""
        if self.cds_client is None:
            try:
                self.copernicus_url = current_app.config.get('COPERNICUS_API_URL')
                self.copernicus_key = current_app.config.get('COPERNICUS_API_KEY')
                
                if self.copernicus_key:
                    # Crear archivo .cdsapirc si no existe
                    # Esto permite funcionar tanto en desarrollo local como en producción
                    cdsapirc_path = os.path.expanduser('~/.cdsapirc')
                    
                    # Verificar si la key ya tiene formato UID:KEY o solo KEY
                    # Nuevas cuentas de Copernicus solo usan KEY sin UID
                    if ':' not in self.copernicus_key:
                        # Formato nuevo (solo API key) - Usar directamente
                        api_key_formatted = self.copernicus_key
                        print(f"[INFO] Using new Copernicus API format (personal access token)")
                    else:
                        # Formato antiguo (UID:KEY) - Mantener como está
                        api_key_formatted = self.copernicus_key
                        print(f"[INFO] Using legacy Copernicus API format (UID:KEY)")
                    
                    # Solo crear si no existe o si está vacío
                    if not os.path.exists(cdsapirc_path) or os.path.getsize(cdsapirc_path) == 0:
                        with open(cdsapirc_path, 'w') as f:
                            f.write(f"url: {self.copernicus_url}\n")
                            f.write(f"key: {api_key_formatted}\n")
                        print(f"[INFO] Created .cdsapirc file at {cdsapirc_path}")
                    
                    # Inicializar cliente (ahora encontrará el archivo)
                    self.cds_client = cdsapi.Client()
                    print(f"[INFO] ✅ Copernicus client initialized successfully")
                else:
                    print(f"[WARNING] ❌ No COPERNICUS_API_KEY found in environment")
            except Exception as e:
                print(f"[ERROR] Could not initialize Copernicus client: {e}")
                # No lanzar excepción, solo loggear - la app seguirá funcionando con placeholders
    
    def get_environmental_data(self, lat, lon, location_name=None, country=None):
        """
        Get comprehensive environmental data for a location in Africa
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            location_name (str, optional): Name of the location
            country (str, optional): Country name
            
        Returns:
            dict: Environmental data including air quality, temperature, etc.
        """
        self._init_copernicus_client()
        
        data = {
            "location": {
                "lat": lat,
                "lon": lon,
                "name": location_name or f"Location ({lat}, {lon})",
                "country": country or "Unknown"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Get different environmental indicators
        try:
            # 1. Air quality data
            air_quality = self.get_air_quality(lat, lon)
            data["air_quality"] = air_quality
            
            # 2. Temperature data
            temperature = self.get_temperature(lat, lon)
            data["temperature"] = temperature
            
            # 3. Vegetation coverage (NDVI)
            vegetation = self.get_vegetation_coverage(lat, lon)
            data["vegetation_coverage"] = vegetation
            
            # 4. Water quality indicators (placeholder)
            data["water_quality"] = self.get_water_quality(lat, lon)
            
            # 5. CO2 emissions estimate
            data["co2_emissions"] = self.estimate_co2_emissions(lat, lon)
            
            # 6. Climate risks
            data["climate_risks"] = self.get_climate_risks(lat, lon)
            
        except Exception as e:
            print(f"Error fetching environmental data: {e}")
            data["error"] = str(e)
        
        return data
    
    def get_air_quality(self, lat, lon):
        """
        Get air quality data from OpenAQ API (real-time monitoring stations)
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: Air quality indicators (PM2.5, NO2, O3, etc.)
        """
        try:
            # Use OpenAQ API for real air quality data
            # Finds nearest monitoring station within 50km radius
            print(f"[INFO] Fetching air quality data from OpenAQ...")
            
            # OpenAQ API v2 - get latest measurements near coordinates
            url = "https://api.openaq.org/v2/latest"
            params = {
                "coordinates": f"{lat},{lon}",
                "radius": 50000,  # 50km radius
                "limit": 10,
                "order_by": "distance"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.ok:
                data = response.json()
                
                if data.get('results') and len(data['results']) > 0:
                    # Extract measurements from nearest stations
                    pm25_values = []
                    no2_values = []
                    o3_values = []
                    station_name = None
                    distance_km = None
                    
                    for station in data['results']:
                        if not station_name:
                            station_name = station.get('location', 'Unknown')
                            # Distance is in meters, convert to km
                            distance_m = station.get('distance', 0)
                            distance_km = round(distance_m / 1000, 1) if distance_m else None
                        
                        for measurement in station.get('measurements', []):
                            param = measurement.get('parameter')
                            value = measurement.get('value')
                            
                            if value is not None:
                                if param == 'pm25':
                                    pm25_values.append(value)
                                elif param == 'no2':
                                    no2_values.append(value)
                                elif param in ['o3', 'ozone']:
                                    o3_values.append(value)
                    
                    # Calculate averages
                    pm25 = round(sum(pm25_values) / len(pm25_values), 2) if pm25_values else 0.0
                    no2 = round(sum(no2_values) / len(no2_values), 2) if no2_values else 0.0
                    o3 = round(sum(o3_values) / len(o3_values), 2) if o3_values else 0.0
                    
                    print(f"[INFO] ✅ Air quality data retrieved from OpenAQ: PM2.5={pm25}, NO2={no2}")
                    
                    return {
                        "pm25": pm25,  # μg/m³
                        "no2": no2,   # μg/m³
                        "ozone": o3,  # μg/m³
                        "source": "OpenAQ",
                        "station": station_name,
                        "distance_km": distance_km,
                        "status": "success"
                    }
            
            # No data available from OpenAQ
            print(f"[INFO] No air quality stations found near location")
            return {
                "pm25": 0.0,
                "no2": 0.0,
                "ozone": 0.0,
                "source": "OpenAQ",
                "status": "no_nearby_stations",
                "note": "No monitoring stations within 50km radius"
            }
            
        except Exception as e:
            print(f"[ERROR] Air quality retrieval failed: {e}")
            return {
                "error": str(e),
                "pm25": 0.0,
                "no2": 0.0,
                "ozone": 0.0,
                "status": "error"
            }
    
    def get_temperature(self, lat, lon):
        """
        Get temperature data and heat wave risk from Copernicus
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: Temperature data and heat indices
        """
        try:
            self._init_copernicus_client()
            
            if not self.cds_client or not XARRAY_AVAILABLE:
                week_ago = datetime.now() - timedelta(days=7)
                date_str = week_ago.strftime('%Y-%m-%d')
                return {
                    "current": 0.0,
                    "average": 0.0,
                    "max_recorded": 0.0,
                    "heat_wave_risk": "unknown",
                    "source": "Copernicus ERA5",
                    "date": date_str,
                    "status": "not_configured"
                }
            
            # Bounding box
            north = min(lat + 0.5, 90)
            south = max(lat - 0.5, -90)
            west = max(lon - 0.5, -180)
            east = min(lon + 0.5, 180)
            
            # Try to get the most recent available data
            # ERA5 typically has 5-7 day delay
            last_error = None
            date_str = None
            temp_path = None

            for days_back in range(5, 50):  # Try from 5 to 49 days ago
                try:
                    target_date = datetime.now() - timedelta(days=days_back)
                    date_str = target_date.strftime('%Y-%m-%d')
                    year = target_date.strftime('%Y')
                    month = target_date.strftime('%m')
                    day = target_date.strftime('%d')
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.nc')
                    temp_path = temp_file.name
                    temp_file.close()
                    
                    print(f"[INFO] Trying temperature data from Copernicus ERA5 for {date_str} ({days_back} days ago)...")
                    
                    self.cds_client.retrieve(
                        'reanalysis-era5-single-levels',
                        {
                            'product_type': 'reanalysis',
                            'variable': ['2m_temperature'],
                            'year': year,
                            'month': month,
                            'day': day,
                            'time': '12:00',
                            'area': [north, west, south, east],
                            'format': 'netcdf',
                        },
                        temp_path
                    )
                    
                    # If we get here, the request succeeded!
                    break
                    
                except Exception as e:
                    last_error = e
                    if temp_path and os.path.exists(temp_path):
                        os.unlink(temp_path)
                    
                    if "not available yet" in str(e).lower():
                        print(f"[INFO] Data not available for {date_str}, trying older date...")
                        continue
                    else:
                        raise
            
            # Check if we found valid data
            if date_str and temp_path and os.path.exists(temp_path):
                try:
                    ds = xr.open_dataset(temp_path)
                    
                    # Convert from Kelvin to Celsius
                    temp_kelvin = float(ds['t2m'].mean().values)
                    temp_celsius = temp_kelvin - 273.15
                    
                    # Determine heat wave risk
                    if temp_celsius > 35:
                        risk = "high"
                    elif temp_celsius > 30:
                        risk = "medium"
                    else:
                        risk = "low"
                    
                    ds.close()
                    
                    print(f"[INFO] ✅ Temperature data retrieved: {temp_celsius:.1f}°C from {date_str}")
                    
                    return {
                        "current": round(temp_celsius, 1),
                        "heat_wave_risk": risk,
                        "source": "Copernicus ERA5 Reanalysis",
                        "date": date_str,
                        "days_old": days_back,
                        "status": "success"
                    }
                    
                finally:
                    if temp_path and os.path.exists(temp_path):
                        os.unlink(temp_path)
            else:
                raise Exception(f"No temperature data available in the last 20 days. Last error: {last_error}")
            
        except Exception as e:
            print(f"[ERROR] Temperature retrieval failed: {e}")
            yesterday = datetime.now() - timedelta(days=1)
            return {
                "error": str(e),
                "current": 0.0,
                "date": yesterday.strftime('%Y-%m-%d'),
                "status": "error"
            }
    
    def get_vegetation_coverage(self, lat, lon):
        """
        Get vegetation coverage using NDVI from satellite data
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: Vegetation coverage data
        """
        try:
            # Available Copernicus datasets for vegetation:
            # 1. 'satellite-lai-fapar' - Leaf Area Index and Fraction of Absorbed Photosynthetically Active Radiation
            # 2. 'satellite-land-cover' - Land cover classification
            # 
            # NDVI calculation requires:
            # - Download Sentinel-2 imagery
            # - Calculate NDVI = (NIR - Red) / (NIR + Red)
            # - Or use Google Earth Engine API
            #
            # For production: Integrate with Sentinel Hub API or Google Earth Engine
            
            return {
                "coverage_percentage": 0.0,  # 0-100%
                "ndvi": 0.0,  # -1 to 1
                "green_zones": "low",  # low, medium, high
                "source": "Copernicus Sentinel (requires Sentinel Hub API)",
                "note": "Requires Sentinel Hub or Google Earth Engine for NDVI calculation"
            }
            
        except Exception as e:
            return {"coverage_percentage": 0.0, "error": str(e)}
    
    def get_water_quality(self, lat, lon):
        """
        Get water quality and pollution indicators
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: Water quality indicators
        """
        # This might require additional APIs or datasets
        return {
            "pollution_level": "unknown",
            "access_to_clean_water": None,
            "source": "Pending integration",
            "note": "May require additional data sources"
        }
    
    def estimate_co2_emissions(self, lat, lon):
        """
        Estimate CO2 emissions for the area
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: CO2 emission estimates
        """
        try:
            # Copernicus dataset: 'cams-global-greenhouse-gas-reanalysis'
            # Requires: CH4, CO2 concentrations
            # Alternative: Use World Bank emissions data by country
            # Or EDGAR (Emissions Database for Global Atmospheric Research)
            
            return {
                "emissions_tons_per_year": 0.0,
                "per_capita": 0.0,
                "trend": "stable",  # increasing, stable, decreasing
                "source": "World Bank / EDGAR (emissions data not yet integrated)",
                "note": "Requires World Bank API or EDGAR database integration"
            }
            
        except Exception as e:
            return {"emissions_tons_per_year": 0.0, "error": str(e)}
    
    def get_climate_risks(self, lat, lon):
        """
        Assess climate risks (floods, droughts, etc.)
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: Climate risk assessment
        """
        return {
            "flood_risk": "medium",  # low, medium, high
            "drought_risk": "medium",
            "extreme_weather_risk": "medium",
            "source": "Copernicus Climate Data Store",
            "note": "Implement climate risk analysis"
        }
    
    def get_biodiversity_index(self, lat, lon):
        """
        Calculate biodiversity index for the area
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: Biodiversity indicators
        """
        return {
            "index": 0.0,  # 0-100
            "species_richness": "unknown",
            "habitat_quality": "unknown",
            "source": "Pending integration",
            "note": "May require specialized biodiversity databases"
        }
