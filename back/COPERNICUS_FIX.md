# Copernicus API Integration - Fix Log

## Fecha: 4 de octubre de 2025

## Problema Original
Los endpoints de temperatura mostraban errores al intentar leer archivos NetCDF descargados de Copernicus Climate Data Store (CDS).

### Error Inicial
```
"error": "did not find a match in any of xarray's currently installed IO backends ['netcdf4', 'cfgrib']"
```

## Diagnóstico

### 1. Verificación de Dependencias
- **xarray**: ✅ Instalado (v2024.7.0)
- **netCDF4**: ✅ Instalado (v1.7.2)
- **cdsapi**: ✅ Instalado (v0.7.7)

### 2. Primer Intento - Especificar Engine
Solución: Agregar `engine='netcdf4'` al abrir archivos con xarray
```python
ds = xr.open_dataset(temp_path, engine='netcdf4')
```
**Resultado**: Error persistió - archivo no era NetCDF válido

### 3. Segundo Intento - Verificar Formato de Archivo
Descubrimiento: El archivo descargado tenía "magic number" `504b0304` que corresponde a **formato ZIP** ("PK")

**Causa Root**: Copernicus CDS devuelve archivos **comprimidos en ZIP** en lugar de NetCDF directo

### 4. Solución Final - Descomprimir Archivos ZIP

#### Cambios Implementados:

1. **Import adicional**:
```python
import zipfile
```

2. **Detección y extracción de ZIP**:
```python
# Verificar magic number
with open(temp_path, 'rb') as f:
    magic = f.read(4)

# Si es ZIP (magic: 504b0304 = "PK")
if magic.startswith(b'PK'):
    # Crear archivo temporal para NetCDF extraído
    extracted_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.nc')
    extracted_path = extracted_temp.name
    extracted_temp.close()
    
    # Extraer .nc del ZIP
    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
        nc_files = [f for f in zip_ref.namelist() if f.endswith('.nc')]
        nc_filename = nc_files[0]
        
        with zip_ref.open(nc_filename) as source:
            with open(extracted_path, 'wb') as target:
                target.write(source.read())
    
    # Limpiar ZIP y usar NetCDF extraído
    os.unlink(temp_path)
    temp_path = extracted_path
```

3. **Abrir NetCDF con engine explícito**:
```python
ds = xr.open_dataset(temp_path, engine='netcdf4')
```

## Estado de Implementación

### ✅ Completado
- Detección automática de archivos ZIP
- Extracción de archivos .nc desde ZIP
- Manejo correcto de archivos temporales en Windows
- Logging detallado del proceso

### 📊 Datos Funcionando
- **Temperatura**: Copernicus ERA5 (variable: `2m_temperature`)
- **Precipitación**: Copernicus ERA5 (variable: `total_precipitation`)
- **CO2 Emissions**: World Bank API
- **Tree Cover**: World Bank API
- **Poverty Index**: World Bank API
- **GDP per capita**: World Bank API
- **Services Access**: World Bank API (electricidad, agua, saneamiento)
- **Unemployment**: World Bank API
- **Water Withdrawal**: World Bank API
- **Health Coverage**: World Bank API

### ⚠️ Pendientes (0.0 values)
- **Air Quality**: OpenAQ (no hay estaciones en locaciones de prueba africanas)
- **Population Density**: WorldPop (requiere descarga de GeoTIFF)
- **UTCI**: Requiere dataset adicional de Copernicus
- **NDVI/Vegetation**: Requiere Sentinel Hub o Google Earth Engine

## Notas Técnicas

### Formato de Archivos Copernicus
- El CDS devuelve archivos en formato **ZIP** por defecto
- Dentro del ZIP hay un archivo `.nc` (NetCDF)
- El NetCDF contiene datos en formato CF-1.7 (Climate and Forecast)

### API Key
- Formato nuevo: Token personal (sin UID:KEY)
- Ejemplo: `c25e9fac-26a7-4096-92c5-471d68b269e5`
- Se guarda en `~/.cdsapirc`

### Latencia de Datos
- ERA5 tiene **5-7 días de latencia**
- El código intenta automáticamente fechas más antiguas si fallan las recientes

## Testing
```bash
# Test simple de temperatura
python test_temperature_simple.py

# Test completo de APIs de África
python tests/test_africa_apis.py
```

## Próximos Pasos
1. Verificar que temperatura y precipitación funcionan correctamente
2. Limpiar logs de debugging una vez confirmado
3. Documentar en API_STATUS.md los indicadores funcionando
4. Considerar implementar UTCI para "sensación térmica"
