"""
Sistema de Pre-carga de Indicadores por País
Genera archivo JSON con todos los indicadores agregados por país
Ejecutar 1 vez al día (cron nocturno)
"""
import json
import os
import sys
import time
import sqlite3
from datetime import datetime, timedelta

# Añadir directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.environmental_service import EnvironmentalService
from services.socioeconomic_service import SocioeconomicService
from flask import Flask

# Países africanos con códigos ISO3
# Para TEST: Solo Egypt
AFRICAN_COUNTRIES_TEST = [
    {"name": "Egypt", "iso3": "EGY"},
]

# Para PRODUCCIÓN: Todos los países de África (SOLO nombre e ISO3 - NO coordenadas de capital)
AFRICAN_COUNTRIES_FULL = [
    {"name": "Nigeria", "iso3": "NGA"},
    {"name": "Kenya", "iso3": "KEN"},
    {"name": "South Africa", "iso3": "ZAF"},
    {"name": "Egypt", "iso3": "EGY"},
    {"name": "Ethiopia", "iso3": "ETH"},
    {"name": "Ghana", "iso3": "GHA"},
    {"name": "Tanzania", "iso3": "TZA"},
    {"name": "Uganda", "iso3": "UGA"},
    {"name": "Algeria", "iso3": "DZA"},
    {"name": "Morocco", "iso3": "MAR"},
    {"name": "Angola", "iso3": "AGO"},
    {"name": "Mozambique", "iso3": "MOZ"},
    {"name": "Madagascar", "iso3": "MDG"},
    {"name": "Cameroon", "iso3": "CMR"},
    {"name": "Ivory Coast", "iso3": "CIV"},
    {"name": "Niger", "iso3": "NER"},
    {"name": "Burkina Faso", "iso3": "BFA"},
    {"name": "Mali", "iso3": "MLI"},
    {"name": "Malawi", "iso3": "MWI"},
    {"name": "Zambia", "iso3": "ZMB"},
    {"name": "Somalia", "iso3": "SOM"},
    {"name": "Senegal", "iso3": "SEN"},
    {"name": "Chad", "iso3": "TCD"},
    {"name": "Zimbabwe", "iso3": "ZWE"},
    {"name": "Guinea", "iso3": "GIN"},
    {"name": "Rwanda", "iso3": "RWA"},
    {"name": "Benin", "iso3": "BEN"},
    {"name": "Tunisia", "iso3": "TUN"},
    {"name": "South Sudan", "iso3": "SSD"},
    {"name": "Togo", "iso3": "TGO"},
]

# Usar lista de test o full según parámetro
AFRICAN_COUNTRIES = AFRICAN_COUNTRIES_TEST  # Cambiar a AFRICAN_COUNTRIES_FULL para producción

def init_database():
    """
    Inicializar base de datos SQLite para persistencia
    Los datos NO se pierden al detener el servidor
    """
    db_path = 'data/country_indicators.db'
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS country_indicators (
            iso3 TEXT PRIMARY KEY,
            country_name TEXT,
            data_json TEXT,
            last_updated TIMESTAMP,
            next_update TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear índice para búsquedas rápidas
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_last_updated 
        ON country_indicators(last_updated)
    ''')
    
    conn.commit()
    conn.close()
    print(f"[INFO] ✅ Base de datos inicializada: {db_path}")
    return db_path

def save_to_database(iso3, country_name, data):
    """
    Guardar datos en SQLite con renovación mensual
    """
    db_path = 'data/country_indicators.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    now = datetime.now()
    # Renovación automática: próxima actualización en 1 mes
    next_update = now + timedelta(days=30)
    
    data_json = json.dumps(data)
    
    cursor.execute('''
        INSERT OR REPLACE INTO country_indicators 
        (iso3, country_name, data_json, last_updated, next_update)
        VALUES (?, ?, ?, ?, ?)
    ''', (iso3, country_name, data_json, now, next_update))
    
    conn.commit()
    conn.close()

def load_from_database(iso3=None):
    """
    Cargar datos desde SQLite
    Si iso3 es None, carga todos los países
    """
    db_path = 'data/country_indicators.db'
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if iso3:
        cursor.execute(
            'SELECT data_json FROM country_indicators WHERE iso3 = ?',
            (iso3,)
        )
        row = cursor.fetchone()
        conn.close()
        return json.loads(row[0]) if row else None
    else:
        cursor.execute('SELECT iso3, data_json FROM country_indicators')
        rows = cursor.fetchall()
        conn.close()
        return {iso3: json.loads(data_json) for iso3, data_json in rows}

def get_countries_needing_update():
    """
    Obtener países que necesitan actualización (pasó 1 mes)
    """
    db_path = 'data/country_indicators.db'
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    now = datetime.now()
    cursor.execute(
        'SELECT iso3, country_name FROM country_indicators WHERE next_update <= ?',
        (now,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def preload_all_countries():
    """
    Pre-carga todos los indicadores para todos los países africanos
    Guarda en SQLite (persistente) y JSON (rápido acceso)
    """
    # Inicializar base de datos
    db_path = init_database()
    
    app = Flask(__name__)
    app.config['COPERNICUS_API_KEY'] = os.getenv('COPERNICUS_API_KEY', 'c25e9fac-26a7-4096-92c5-471d68b269e5')
    app.config['COPERNICUS_API_URL'] = 'https://cds.climate.copernicus.eu/api'
    
    print("=" * 100)
    print(f"INICIANDO PRE-CARGA DE DATOS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Países a procesar: {len(AFRICAN_COUNTRIES)}")
    print(f"Base de datos: {db_path}")
    print("=" * 100)
    
    results = {}
    
    with app.app_context():
        env_service = EnvironmentalService()
        soc_service = SocioeconomicService()
        
        for i, country in enumerate(AFRICAN_COUNTRIES):
            print(f"\n[{i+1}/{len(AFRICAN_COUNTRIES)}] Procesando {country['name']} ({country['iso3']})...")
            start_time = time.time()
            
            try:
                # DATOS AMBIENTALES (servicio simplificado para producción rápida)
                env_data = env_service.get_country_environmental_data(
                    country['iso3'],
                    country['name']
                )
                
                # Datos socioeconómicos (ya son por país)
                soc_data = soc_service.get_country_socioeconomic_data(
                    country['iso3'],
                    country['name']
                )
                
                # Combinar resultados
                results[country['iso3']] = {
                    'country_name': country['name'],
                    'iso3': country['iso3'],
                    'aggregation_method': 'MIXED_SOURCES_PRODUCTION_READY',
                    'indicators': {
                        # Environmental (4)
                        'temperature_avg_celsius': env_data.get('temperature', {}).get('annual_mean', 0),
                        'precipitation_annual_mm': env_data.get('precipitation', {}).get('annual_total', 0),
                        'co2_ppm': env_data.get('co2', {}).get('annual_mean', 0),
                        'forest_cover_pct': env_data.get('forest', {}).get('forest_percentage', 0),
                        
                        # Socioeconomic (7)
                        'population_density': soc_data.get('population', {}).get('density_per_km2', 0),
                        'poverty_rate_pct': soc_data.get('poverty_index', {}).get('percentage_below_poverty_line', 0),
                        'water_withdrawal_pct': soc_data.get('water_withdrawal', {}).get('withdrawal_percentage', 0),
                        'school_enrollment_pct': soc_data.get('school_enrollment', {}).get('enrollment_rate', 0),
                        'unemployment_pct': soc_data.get('unemployment', {}).get('unemployment_rate', 0),
                        'received_wages_pct': soc_data.get('received_wages', {}).get('received_wages_pct', 0),
                        'health_coverage_index': soc_data.get('health_coverage', {}).get('health_coverage_index', 0),
                    },
                    'metadata': {
                        'temperature_year': env_data.get('temperature', {}).get('year'),
                        'co2_year': env_data.get('co2', {}).get('year'),
                        'forest_year': env_data.get('forest', {}).get('year'),
                        'last_updated': datetime.now().isoformat(),
                        'processing_time_seconds': round(time.time() - start_time, 2)
                    }
                }
                
                elapsed = time.time() - start_time
                print(f"   ✅ Completado en {elapsed:.1f}s")
                
                # Guardar en SQLite (persistente)
                save_to_database(country['iso3'], country['name'], results[country['iso3']])
                print(f"   💾 Guardado en base de datos")
                
                # Delay entre países para evitar rate limits
                if i < len(AFRICAN_COUNTRIES) - 1:
                    print(f"   ⏳ Esperando 15s antes del siguiente país...")
                    time.sleep(15)
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results[country['iso3']] = {
                    'country_name': country['name'],
                    'iso3': country['iso3'],
                    'error': str(e),
                    'metadata': {
                        'last_updated': datetime.now().isoformat(),
                        'processing_time_seconds': round(time.time() - start_time, 2)
                    }
                }
    
    # Guardar resultados en JSON (backup + acceso rápido)
    output_file = 'data/country_indicators.json'
    os.makedirs('data', exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 100)
    print(f"✅ PRE-CARGA COMPLETADA")
    print(f"SQLite: {db_path} (PERSISTENTE - no se pierde al parar)")
    print(f"JSON: {output_file} (backup + acceso rápido)")
    print(f"Países procesados: {len([r for r in results.values() if 'error' not in r])}/{len(AFRICAN_COUNTRIES)}")
    print(f"Próxima actualización automática: En 30 días")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    
    return results

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Pre-cargar datos de indicadores por país')
    parser.add_argument('--full', action='store_true', help='Procesar todos los países de África (por defecto: solo Egypt)')
    args = parser.parse_args()
    
    # Cambiar lista de países según argumento
    if args.full:
        print("[INFO] Modo FULL: Procesando todos los países de África")
        AFRICAN_COUNTRIES = AFRICAN_COUNTRIES_FULL
    else:
        print("[INFO] Modo TEST: Procesando solo Egypt")
        AFRICAN_COUNTRIES = AFRICAN_COUNTRIES_TEST
    
    preload_all_countries()
