# 🌍 Guía de Integración de APIs - Enfoque en África

## 📋 APIs Configuradas

### 1. Copernicus Climate Data Store (CDS) - Datos Ambientales
### 2. WorldPop SDI API - Datos Socioeconómicos

---

## 🔑 Obtener API Keys

### Copernicus CDS (REQUERIDO)

**1. Crear cuenta:**
- Ve a: https://cds.climate.copernicus.eu/user/register
- Completa el formulario de registro
- Confirma tu email

**2. Aceptar términos:**
- Una vez logueado, ve a: https://cds.climate.copernicus.eu/how-to-api
- Lee y acepta los términos de uso

**3. Obtener API Key:**
- En tu perfil: https://cds.climate.copernicus.eu/user
- Verás tu UID y API Key
- Formato: `{uid}:{api-key}`
- Ejemplo: `12345:abcd1234-ef56-7890-gh12-ijklmnopqr34`

**4. Configurar:**
```bash
# Copia .env.example a .env
cp .env.example .env

# Edita .env y agrega tu key:
COPERNICUS_API_KEY=12345:abcd1234-ef56-7890-gh12-ijklmnopqr34
```

### WorldPop (NO REQUIERE API KEY)

La API de WorldPop es pública para consultas básicas.
- Documentación: https://www.worldpop.org/sdi/introapi/
- No necesitas registrarte para usar los endpoints básicos

---

## 📊 Datos que Obtendrás

### 🌡️ Datos Ambientales (Copernicus)

**Endpoint:** `GET /api/environmental?lat=6.5244&lon=3.3792&country=Nigeria`

**Datos incluidos:**
```json
{
  "air_quality": {
    "pm25": 45.2,        // Partículas PM2.5 (μg/m³)
    "no2": 38.5,         // Dióxido de nitrógeno
    "ozone": 62.1,       // Ozono
    "so2": 15.3,         // Dióxido de azufre
    "co": 0.8            // Monóxido de carbono
  },
  "temperature": {
    "current": 28.5,     // Temperatura actual (°C)
    "average": 27.2,     // Promedio mensual
    "heat_wave_risk": "medium"
  },
  "vegetation_coverage": {
    "coverage_percentage": 35.2,  // % de cobertura vegetal
    "ndvi": 0.65,                 // Índice de vegetación (-1 a 1)
    "green_zones": "medium"
  },
  "water_quality": {
    "pollution_level": "medium",
    "access_to_clean_water": 72
  },
  "co2_emissions": {
    "emissions_tons_per_year": 8.2,
    "per_capita": 0.4,
    "trend": "increasing"
  },
  "climate_risks": {
    "flood_risk": "high",
    "drought_risk": "medium",
    "extreme_weather_risk": "medium"
  }
}
```

### 👥 Datos Socioeconómicos (WorldPop)

**Endpoint:** `GET /api/socioeconomic?lat=6.5244&lon=3.3792&country=Nigeria`

**Datos incluidos:**
```json
{
  "population": {
    "total": 12500,
    "density_per_km2": 450.5,
    "growth_rate": 2.8,
    "age_distribution": {
      "0-14": 45,
      "15-64": 52,
      "65+": 3
    }
  },
  "poverty_index": {
    "index": 45.2,       // 0-100 (más alto = más pobreza)
    "percentage_below_poverty_line": 38.5,
    "gini_coefficient": 0.42
  },
  "basic_services_access": {
    "water": 68,         // % con acceso a agua limpia
    "health": 52,        // % con acceso a salud
    "education": 71,     // % con acceso a educación
    "electricity": 45,
    "sanitation": 38
  },
  "average_income": {
    "average_annual_usd": 3200,
    "median_annual_usd": 2100,
    "economic_activity_level": "medium"
  },
  "human_development_index": {
    "index": 0.48,       // 0-1 (más alto = mejor desarrollo)
    "components": {
      "health": 0.55,
      "education": 0.42,
      "income": 0.47
    },
    "classification": "low"
  }
}
```

---

## 🚀 Cómo Usar

### 1. Instalar dependencias

```powershell
cd back
pip install -r requirements.txt
```

Esto instalará:
- `cdsapi` - Cliente oficial de Copernicus
- `requests` - Para llamadas HTTP (WorldPop)

### 2. Configurar API Key

```bash
# Crear archivo .env
cp .env.example .env

# Editar con tu Copernicus API key
# COPERNICUS_API_KEY=tu_uid:tu_api_key
```

### 3. Ejecutar servidor

```powershell
python app.py
```

### 4. Probar endpoints

```bash
# Lagos, Nigeria
curl "http://localhost:5000/api/environmental?lat=6.5244&lon=3.3792&country=Nigeria"

# Nairobi, Kenya
curl "http://localhost:5000/api/environmental?lat=-1.2921&lon=36.8219&country=Kenya"

# Ciudad del Cabo, Sudáfrica
curl "http://localhost:5000/api/environmental?lat=-33.9249&lon=18.4241&country=South%20Africa"
```

---

## 🗺️ Ubicaciones de Ejemplo en África

```javascript
// Lagos, Nigeria
{lat: 6.5244, lon: 3.3792, name: "Lagos", country: "Nigeria"}

// Nairobi, Kenya
{lat: -1.2921, lon: 36.8219, name: "Nairobi", country: "Kenya"}

// Ciudad del Cabo, Sudáfrica
{lat: -33.9249, lon: 18.4241, name: "Cape Town", country: "South Africa"}

// Cairo, Egipto
{lat: 30.0444, lon: 31.2357, name: "Cairo", country: "Egypt"}

// Addis Ababa, Etiopía
{lat: 9.0320, lon: 38.7469, name: "Addis Ababa", country: "Ethiopia"}

// Dar es Salaam, Tanzania
{lat: -6.7924, lon: 39.2083, name: "Dar es Salaam", country: "Tanzania"}

// Accra, Ghana
{lat: 5.6037, lon: -0.1870, name: "Accra", country: "Ghana"}

// Kinshasa, RD Congo
{lat: -4.4419, lon: 15.2663, name: "Kinshasa", country: "DR Congo"}
```

---

## 🔧 Implementación Paso a Paso

### Paso 1: Copernicus CDS - Calidad del Aire

Los servicios están en `services/environmental_service.py`. Para implementar datos reales:

```python
def get_air_quality(self, lat, lon):
    """Obtener calidad del aire real de Copernicus CAMS"""
    
    if not self.cds_client:
        self._init_copernicus_client()
    
    # Dataset: cams-global-atmospheric-composition-forecasts
    result = self.cds_client.retrieve(
        'cams-global-atmospheric-composition-forecasts',
        {
            'variable': ['particulate_matter_2.5um', 'nitrogen_dioxide', 'ozone'],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': '12:00',
            'leadtime_hour': '0',
            'type': 'forecast',
            'area': [lat+0.1, lon-0.1, lat-0.1, lon+0.1],  # Bounding box
            'format': 'netcdf',
        }
    )
    
    # Procesar resultado NetCDF...
    return processed_data
```

### Paso 2: WorldPop - Población

```python
def get_population_data(self, lat, lon, country):
    """Obtener datos de población de WorldPop"""
    
    # Endpoint: /v1/wopr/pointtotal
    url = f"{self.worldpop_url}/v1/wopr/pointtotal"
    
    params = {
        'iso3': self._get_iso3_code(country),  # NGA, KEN, etc.
        'lat': lat,
        'lon': lon
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    return {
        "total": data.get('total_population'),
        "density_per_km2": data.get('density'),
        "source": "WorldPop"
    }
```

---

## 📝 TODOs Pendientes

### Implementación Completa

- [ ] **Copernicus CAMS** - Calidad del aire (PM2.5, NO2, O3)
- [ ] **Copernicus ERA5** - Temperatura y clima
- [ ] **Copernicus Land** - Cobertura vegetal (NDVI)
- [ ] **Copernicus GHG** - Emisiones de CO2
- [ ] **WorldPop Point** - Población por coordenadas
- [ ] **WorldPop Accessibility** - Acceso a servicios

### Procesamiento de Datos

- [ ] Parsear archivos NetCDF de Copernicus
- [ ] Calcular índices compuestos (IVSA)
- [ ] Agregar datos históricos (tendencias)
- [ ] Implementar caché por región

### Optimización

- [ ] Caché de consultas frecuentes
- [ ] Batch requests para múltiples ubicaciones
- [ ] Fallback a datos cached si API falla
- [ ] Rate limiting específico por API

---

## 🆘 Troubleshooting

### Error: "Invalid API key"
- Verifica que copiaste correctamente el UID:API-KEY de Copernicus
- Formato: `12345:abcdef12-3456-7890-abcd-ef1234567890`
- Sin espacios ni comillas

### Error: "Request failed"
- Verifica tu conexión a internet
- Copernicus puede estar en mantenimiento
- Revisa límites de uso (hay cuotas diarias)

### Error: "No data available"
- Algunos datasets de Copernicus tienen cobertura limitada
- Verifica que las coordenadas sean válidas para África
- Algunos datos históricos pueden no estar disponibles

### WorldPop no responde
- La API es pública pero puede tener rate limits
- Usa coordenadas válidas dentro de países africanos
- Algunos países pueden no tener todos los datasets

---

## 📚 Recursos

### Copernicus
- Portal principal: https://cds.climate.copernicus.eu/
- Documentación API: https://cds.climate.copernicus.eu/how-to-api
- Datasets disponibles: https://cds.climate.copernicus.eu/cdsapp#!/search?type=dataset
- Tutoriales: https://cds.climate.copernicus.eu/tutorial

### WorldPop
- Portal: https://www.worldpop.org/
- API Docs: https://www.worldpop.org/sdi/introapi/
- Datasets: https://www.worldpop.org/methods/populations
- GitHub: https://github.com/wpgp

### Otros recursos útiles
- ISO 3166 Country Codes: https://www.iso.org/obp/ui/#search
- GeoJSON para África: http://geojson.xyz/
- OpenStreetMap África: https://www.openstreetmap.org/

---

¡Listo para obtener datos reales de África! 🌍
