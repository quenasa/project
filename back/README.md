# Climate and Social Justice Map - Backend API

Backend API modular para el proyecto de Mapa de Justicia Climática y Social (NASA Space Apps Challenge 2025).  
**Enfoque regional: África** 🌍

## 🚀 Quick Start (3 pasos)

### 1️⃣ Instalar dependencias
```powershell
cd back
pip install -r requirements.txt
```

### 2️⃣ Configurar API keys
```powershell
# Copia el archivo de ejemplo
cp .env.example .env

# Edita .env con tus claves:
# - COPERNICUS_API_KEY (Copernicus CDS)
# - Consulta API_AFRICA_SETUP.md para obtener las claves
```

### 3️⃣ Ejecutar servidor
```powershell
python app.py
```

✅ **Verificar que funciona**:
```powershell
# En otra terminal
python tests/test_africa_apis.py
```

---

## 🏗️ Arquitectura Modular

```
back/
├── app.py                 # Aplicación principal (Factory Pattern)
├── config/                # Configuración
│   ├── __init__.py
│   └── settings.py       # Settings por entorno (dev, prod, test)
├── api/                   # Rutas/Controllers
│   ├── routes.py         # Rutas principales
│   ├── environmental_routes.py
│   ├── socioeconomic_routes.py
│   ├── democratic_routes.py
│   ├── vulnerability_routes.py
│   └── reports_routes.py
├── services/              # Lógica de negocio
│   ├── environmental_service.py   # Copernicus CDS
│   ├── socioeconomic_service.py   # WorldPop
│   ├── democratic_service.py
│   ├── vulnerability_service.py
│   └── reports_service.py
├── tests/                 # Tests y datos mock
│   ├── test_africa_apis.py        # Tests para África
│   ├── test_integration.py
│   └── mock_data.py      
└── requirements.txt
```

## 🌟 Características

- ✅ **Arquitectura modular** - Separación de concerns (routes, services, config)
- ✅ **Rate Limiting** - 200 req/día, 50 req/hora (Flask-Limiter)
- ✅ **Caché** - 1 hora de caché para reducir llamadas a APIs (Flask-Caching)
- ✅ **OpenStreetMap Ready** - Coordenadas en formato lat/lon
- ✅ **Enfoque África** - Validación de coordenadas región africana
- ✅ **Copernicus CDS** - Datos ambientales (clima, aire, temperatura)
- ✅ **WorldPop API** - Datos socioeconómicos (población, demografía)
- ✅ **Datos actuales** - Llamadas a APIs con fecha de hoy
- ✅ **Auto-configuración** - Crea `.cdsapirc` automáticamente desde `.env`
- ✅ **CORS habilitado** - Listo para integrar con frontend
- ✅ **Listo para deploy** - Funciona en local y en servidores web
- ✅ **Factory Pattern** - Creación de app con diferentes configuraciones

## 📡 APIs Integradas

### 1. Copernicus Climate Data Store (CDS)
- **Datos ambientales**: Calidad del aire, temperatura, vegetación, CO2
- **Datasets**: CAMS, ERA5, Sentinel
- **Cobertura**: Global con enfoque en África
- **Setup**: Ver `API_AFRICA_SETUP.md`

### 2. WorldPop Spatial Data Infrastructure
- **Datos socioeconómicos**: Población, densidad, demografía
- **Datasets**: Population counts, age/sex structure
- **Cobertura**: África completa
- **Setup**: Ver `API_AFRICA_SETUP.md`

## 🌍 Endpoints Disponibles

### Salud del servidor
```
GET /api/health
```

### Datos ambientales (requiere coordenadas)
```
GET /api/environmental?lat=-1.286389&lon=36.817223
```
Respuesta: calidad del aire, temperatura, vegetación, riesgos climáticos

### Datos socioeconómicos (requiere coordenadas)
```
GET /api/socioeconomic?lat=-1.286389&lon=36.817223
```
Respuesta: población, pobreza, acceso a servicios, HDI

### Datos democráticos (requiere país)
```
GET /api/democratic?country=Kenya
```
Respuesta: participación electoral, transparencia, espacios ciudadanos

### Índice de vulnerabilidad (requiere coordenadas)
```
GET /api/vulnerability/ivsa?lat=-1.286389&lon=36.817223
```
Respuesta: IVSA calculado + componentes

### Reportes ciudadanos
```
GET    /api/reports           # Listar todos
POST   /api/reports           # Crear nuevo
GET    /api/reports/<id>      # Ver detalle
PUT    /api/reports/<id>      # Actualizar
```

## 🧪 Testing

### Tests de integración África
```powershell
python tests/test_africa_apis.py
```
Prueba 4 ubicaciones en África:
- Lagos, Nigeria
- Nairobi, Kenya
- Cape Town, South Africa
- Cairo, Egypt

### Tests generales
```powershell
python tests/test_integration.py
```

## 📁 Dónde está cada cosa

| Necesito... | Está en... |
|------------|-----------|
| Crear un endpoint | `api/*_routes.py` |
| Añadir lógica de negocio | `services/*_service.py` |
| Cambiar configuración | `config/settings.py` |
| Agregar tests | `tests/test_*.py` |
| Datos de ejemplo | `tests/mock_data.py` |

## ⚙️ Configuración

### Variables de entorno (`.env`)

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
HOST=0.0.0.0

# Copernicus Climate Data Store
COPERNICUS_API_KEY=tu_clave_aqui
COPERNICUS_API_URL=https://cds.climate.copernicus.eu/api/v2

# WorldPop Spatial Data Infrastructure
WORLDPOP_API_URL=https://www.worldpop.org/sdi/api
```

Ver **`API_AFRICA_SETUP.md`** para instrucciones detalladas de obtención de claves.

## � Deploy en Producción

El backend está **listo para desplegar** en cualquier servidor. Solo necesitas:

1. **Variables de entorno** en el servidor:
   - `COPERNICUS_API_KEY` - Tu clave de Copernicus
   - `COPERNICUS_API_URL` - URL de la API (por defecto: https://cds.climate.copernicus.eu/api)
   - `WORLDPOP_API_URL` - URL de WorldPop (por defecto: https://www.worldpop.org/sdi/api)

2. **Auto-configuración**: El backend **crea automáticamente** el archivo `.cdsapirc` desde las variables de entorno, por lo que funciona tanto en:
   - ✅ Local (Windows, macOS, Linux)
   - ✅ Heroku
   - ✅ AWS (EC2, Lambda, Elastic Beanstalk)
   - ✅ DigitalOcean
   - ✅ Google Cloud
   - ✅ Azure

3. **No necesitas configurar nada más** - Solo las variables de entorno

## �🔧 Comandos útiles

```powershell
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor (desarrollo)
python app.py

# Ejecutar tests
python tests/test_africa_apis.py

# Ver logs del servidor
# (automáticamente en consola con DEBUG=True)

# Generar requirements.txt
pip freeze > requirements.txt
```

## 📚 Documentación Adicional

- **`API_AFRICA_SETUP.md`** - Guía completa de configuración de APIs para África
- **`.env.example`** - Plantilla de variables de entorno

## 🛠️ Stack Tecnológico

- **Flask 3.0.0** - Web framework
- **Flask-CORS 4.0.0** - Cross-Origin Resource Sharing
- **Flask-Limiter 3.5.0** - Rate limiting
- **Flask-Caching 2.1.0** - Response caching
- **cdsapi 0.6.1** - Copernicus CDS client
- **requests 2.31.0** - HTTP library
- **python-dotenv 1.0.0** - Environment variables

## 📈 Rate Limiting

| Tipo | Límite |
|------|--------|
| Global | 200 req/día |
| Lectura (GET) | 50 req/hora |
| Escritura (POST/PUT) | 30 req/hora |

## 🗺️ Validación Geográfica

El backend valida que las coordenadas estén dentro de la región africana:
- **Latitud**: -35 a 37
- **Longitud**: -20 a 55

Fuera de estos rangos, retorna error 400.

## 🐛 Troubleshooting

### Error: "API not configured"
- Verifica que tienes `COPERNICUS_API_KEY` en tu `.env`
- Consulta `API_AFRICA_SETUP.md` para obtener la clave

### Error: "Rate limit exceeded"
- Espera 1 hora o ajusta los límites en `config/settings.py`

### Error: "Coordinates outside Africa region"
- Verifica que lat/lon están dentro del rango africano
- Ejemplo válido: Lagos `lat=6.5244, lon=3.3792`

## 📝 Notas

- Los datos ambientales y socioeconómicos requieren claves de API configuradas
- Las llamadas a APIs usan **la fecha actual** para obtener los datos más recientes
- El caché es de **1 hora** para optimizar rendimiento
- Los reportes ciudadanos se almacenan en memoria (temporal)

---

**Proyecto**: NASA Space Apps Challenge 2025  
**Enfoque**: Justicia climática y social en África
python app.py
```

El servidor estará disponible en `http://localhost:5000`

## 🧪 Testing

Ejecutar tests de integración:
```powershell
python tests/test_integration.py
```

Los tests verifican:
- ✅ Endpoints principales (health, root)
- ✅ Reportes ciudadanos (CRUD completo)
- ✅ Endpoints de datos (verifican que retornan 501 Not Implemented)

## 📡 API Endpoints

### Estado
- `GET /` - Información de la API
- `GET /api/health` - Health check

### Datos (Requieren integración con APIs externas)
- `GET /api/environmental?location=Madrid&country=Spain`
- `GET /api/socioeconomic?location=Madrid&country=Spain`
- `GET /api/democratic?location=Madrid&country=Spain`
- `GET /api/vulnerability` - Índice IVSA calculado

### Reportes Ciudadanos (Funcional)
- `GET /api/reports` - Listar reportes
- `GET /api/reports?type=illegal_dump` - Filtrar por tipo
- `POST /api/reports` - Crear reporte
- `GET /api/reports/{id}` - Obtener reporte específico
- `PUT /api/reports/{id}` - Actualizar estado

## 🔌 Estado de Integración

### ✅ Implementado
- Sistema de reportes ciudadanos
- Rate limiting y caché
- Arquitectura modular
- OpenStreetMap ready (lat/lon)

### ⏳ Pendiente (Requiere APIs externas)
- **Environmental**: OpenAQ, NASA Earthdata, Copernicus
- **Socioeconomic**: World Bank, UN Data
- **Democratic**: Electoral commissions, civic databases
- **Vulnerability**: Cálculo automático del IVSA

Ver `API_INTEGRATION_GUIDE.md` para detalles de implementación.

## 📊 Datos de Prueba

Los datos mock están en `tests/mock_data.py` con 5 ubicaciones de ejemplo:
- Madrid Sur - Vallecas (España)
- Barcelona - Gràcia (España)
- Nueva Delhi (India)
- Jakarta (Indonesia)
- São Paulo (Brasil)

**Nota**: Estos datos son SOLO para testing. El sistema está diseñado para obtener datos dinámicamente de APIs externas.

## 🌍 OpenStreetMap Integration

Todas las coordenadas están en formato estándar para OpenStreetMap:
```json
{
  "lat": 40.4168,
  "lon": -3.7038,
  "name": "Location Name",
  "country": "Country"
}
```

El frontend puede usar directamente estas coordenadas con Leaflet.js u otras librerías de mapas.

## 🔐 Rate Limiting

- **Endpoints generales**: 200 req/día, 50 req/hora
- **Reportes (POST)**: 30 req/hora
- **Health/Root**: Sin límite

## 💾 Caché

- **Duración**: 1 hora
- **Tipo**: Simple (en memoria)
- **Incluye**: Query parameters en la clave de caché

Para producción, considera usar Redis:
```python
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
```

## 📝 Próximos Pasos

1. **Base de Datos**: Agregar PostgreSQL/MongoDB para persistencia
2. **APIs Externas**: Integrar OpenAQ, NASA, World Bank
3. **Autenticación**: JWT para usuarios
4. **Logging**: Estructurado con niveles
5. **Tests Unitarios**: pytest con coverage
6. **CI/CD**: GitHub Actions
7. **Deployment**: Railway/Heroku/AWS

## 🤝 Contribuir

1. La arquitectura es modular - cada servicio es independiente
2. Los datos mock van SOLO en `tests/`
3. La lógica de negocio va en `services/`
4. Las rutas van en `api/`
5. La configuración va en `config/`

## 📚 Documentación Adicional

- `API_INTEGRATION_GUIDE.md` - Cómo integrar APIs externas
- `BACKEND_README.md` - Documentación original (deprecated)
- `.env.example` - Variables de entorno requeridas

## 🎯 Para el equipo de Frontend

El backend está listo para:
- Recibir coordenadas lat/lon para OpenStreetMap
- CORS habilitado para peticiones cross-origin
- Endpoints de reportes completamente funcionales
- Rate limiting configurado

Los endpoints de datos (environmental, socioeconomic, democratic) retornan `501 Not Implemented` hasta que se integren las APIs externas.
