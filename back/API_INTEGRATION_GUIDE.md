# External API Integration Guide

This guide explains how to integrate real external data sources into the Climate and Social Justice Map backend.

## 🌐 Available Data Sources

### 1. Environmental Data APIs

#### OpenAQ - Air Quality Data
- **Website**: https://openaq.org/
- **API Docs**: https://docs.openaq.org/
- **Free Tier**: Yes
- **Data**: PM2.5, NO2, O3, SO2, CO, PM10

**Example Integration**:
```python
import requests

def get_air_quality(city, country):
    url = "https://api.openaq.org/v2/latest"
    params = {
        "city": city,
        "country": country,
        "limit": 100
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### NASA Earthdata
- **Website**: https://earthdata.nasa.gov/
- **API Key**: Required (free)
- **Data**: Temperature, vegetation, fires, floods

**Example Integration**:
```python
def get_nasa_data(lat, lon, dataset):
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "latitude": lat,
        "longitude": lon,
        "parameters": dataset,
        "community": "AG",
        "format": "JSON"
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### Copernicus Climate Data Store
- **Website**: https://cds.climate.copernicus.eu/
- **API Key**: Required (free)
- **Data**: Climate reanalysis, temperature, precipitation

### 2. Socioeconomic Data APIs

#### World Bank API
- **Website**: https://data.worldbank.org/
- **API Docs**: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
- **Free Tier**: Yes
- **Data**: GDP, poverty, education, health indicators

**Example Integration**:
```python
def get_world_bank_data(country, indicator):
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {
        "format": "json",
        "per_page": 100
    }
    response = requests.get(url, params=params)
    return response.json()

# Example indicators:
# SI.POV.DDAY - Poverty headcount ratio
# NY.GDP.PCAP.CD - GDP per capita
# SE.PRM.ENRR - School enrollment
```

#### UN Data API
- **Website**: https://data.un.org/
- **Free Tier**: Yes
- **Data**: Human development index, demographics

### 3. Government Open Data Portals

#### Spain - datos.gob.es
- **Website**: https://datos.gob.es/
- **API Docs**: https://datos.gob.es/en/developers
- **Data**: Various government datasets

#### European Data Portal
- **Website**: https://data.europa.eu/
- **Data**: EU-wide datasets

## 🔌 Implementation Example

Here's how to modify `app.py` to use real APIs:

### Step 1: Create API Client Module

Create a new file `api_clients.py`:

```python
import requests
import os
from datetime import datetime
from functools import lru_cache

class OpenAQClient:
    """Client for OpenAQ Air Quality API"""
    BASE_URL = "https://api.openaq.org/v2"
    
    @lru_cache(maxsize=100)
    def get_latest_measurements(self, city, country="ES"):
        """Get latest air quality measurements for a city"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/latest",
                params={
                    "city": city,
                    "country": country,
                    "limit": 100
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching OpenAQ data: {e}")
            return None

class NASAClient:
    """Client for NASA POWER API"""
    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    def __init__(self, api_key=None):
        self.api_key = api_key
    
    @lru_cache(maxsize=100)
    def get_climate_data(self, lat, lon):
        """Get climate data for coordinates"""
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "parameters": "T2M,PRECTOTCORR",  # Temperature, Precipitation
                "community": "AG",
                "format": "JSON",
                "start": "20240101",
                "end": "20241231"
            }
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching NASA data: {e}")
            return None

class WorldBankClient:
    """Client for World Bank API"""
    BASE_URL = "https://api.worldbank.org/v2"
    
    @lru_cache(maxsize=100)
    def get_indicator(self, country, indicator):
        """Get World Bank indicator data"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/country/{country}/indicator/{indicator}",
                params={"format": "json", "per_page": 100},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data[1] if len(data) > 1 else []
        except Exception as e:
            print(f"Error fetching World Bank data: {e}")
            return []
```

### Step 2: Update app.py to Use Real APIs

Modify the endpoints in `app.py`:

```python
from api_clients import OpenAQClient, NASAClient, WorldBankClient

# Initialize clients
openaq = OpenAQClient()
nasa = NASAClient(api_key=os.getenv('NASA_API_KEY'))
world_bank = WorldBankClient()

@app.route('/api/environmental')
def get_environmental_data():
    """Get real environmental data from APIs"""
    location = request.args.get('location', 'Madrid')
    
    # Get air quality from OpenAQ
    air_quality = openaq.get_latest_measurements(location, country="ES")
    
    # Process and return data
    if air_quality and air_quality.get('results'):
        data = process_air_quality_data(air_quality['results'])
        return jsonify({"data": data, "count": len(data)})
    
    # Fallback to mock data if API fails
    return jsonify({"data": MOCK_ENVIRONMENTAL_DATA, "count": len(MOCK_ENVIRONMENTAL_DATA)})
```

### Step 3: Add Caching

To avoid hitting API rate limits, implement caching:

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 3600  # 1 hour
})

@app.route('/api/environmental')
@cache.cached(timeout=3600, query_string=True)
def get_environmental_data():
    # Your API calls here
    pass
```

### Step 4: Add Error Handling

```python
from functools import wraps

def handle_api_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.Timeout:
            return jsonify({"error": "API timeout"}), 504
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 503
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    return decorated_function

@app.route('/api/environmental')
@handle_api_errors
def get_environmental_data():
    # Your code here
    pass
```

## 🔐 Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Rate limiting** - Implement rate limiting to prevent abuse
3. **Input validation** - Always validate user inputs
4. **HTTPS only** - Use HTTPS in production
5. **API key rotation** - Regularly rotate API keys

## 📊 Data Processing Tips

### Normalize Data
```python
def normalize_score(value, min_val, max_val):
    """Normalize value to 0-100 scale"""
    return ((value - min_val) / (max_val - min_val)) * 100
```

### Handle Missing Data
```python
def fill_missing_data(data, default=0):
    """Fill missing values with default"""
    return {k: v if v is not None else default for k, v in data.items()}
```

### Aggregate Data
```python
from statistics import mean

def aggregate_measurements(measurements):
    """Calculate averages from multiple measurements"""
    return {
        "pm25": mean([m['pm25'] for m in measurements if 'pm25' in m]),
        "no2": mean([m['no2'] for m in measurements if 'no2' in m])
    }
```

## 🧪 Testing with Real APIs

Create a test script `test_external_apis.py`:

```python
import unittest
from api_clients import OpenAQClient, NASAClient, WorldBankClient

class TestExternalAPIs(unittest.TestCase):
    def setUp(self):
        self.openaq = OpenAQClient()
        self.nasa = NASAClient()
        self.world_bank = WorldBankClient()
    
    def test_openaq_connection(self):
        data = self.openaq.get_latest_measurements("Madrid")
        self.assertIsNotNone(data)
        self.assertIn('results', data)
    
    def test_nasa_connection(self):
        data = self.nasa.get_climate_data(40.4168, -3.7038)
        self.assertIsNotNone(data)
    
    def test_world_bank_connection(self):
        data = self.world_bank.get_indicator("ES", "SI.POV.DDAY")
        self.assertIsInstance(data, list)

if __name__ == '__main__':
    unittest.main()
```

## 📈 Monitoring and Logging

Add logging to track API usage:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_environmental_data():
    logger.info(f"Fetching environmental data for location: {location}")
    # Your code here
    logger.info(f"Successfully fetched {len(data)} records")
```

## 🚀 Next Steps

1. Implement database caching with PostgreSQL + PostGIS
2. Add background jobs with Celery for periodic data updates
3. Implement WebSocket for real-time data streaming
4. Add authentication for premium features
5. Deploy to cloud (AWS, GCP, or Azure)

## 📚 Additional Resources

- [OpenAQ Documentation](https://docs.openaq.org/)
- [NASA API Documentation](https://power.larc.nasa.gov/docs/)
- [World Bank API Guide](https://datahelpdesk.worldbank.org/knowledgebase/topics/125589)
- [Flask Best Practices](https://flask.palletsprojects.com/en/latest/patterns/)
- [RESTful API Design](https://restfulapi.net/)
