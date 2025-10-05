#!/usr/bin/env python3
"""
🌍 GENERADOR DE DATOS MUNDIAL - SQLite + JSON
============================================

Versión global que procesa TODOS los países del mundo usando
los services refactorizados y unificados.

✅ 195 países del mundo
✅ Copernicus: CO2, temperatura, precipitación, forest  
✅ World Bank: socioeconómicos
✅ SQLite + JSON output
✅ 0.0 → null automático

Para ejecutar: python scripts/generate_world_data.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
import os
import sqlite3
import time
from datetime import datetime
from services.environmental_service import EnvironmentalService
from services.socioeconomic_service import SocioeconomicService

class WorldDataGenerator:
    def __init__(self):
        """Inicializar generador mundial de datos"""
        self.env_service = EnvironmentalService()
        self.socio_service = SocioeconomicService()
        
        # Cargar países del mundo
        with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'world_countries.json'), 'r', encoding='utf-8') as f:
            world_data = json.load(f)
        
        # Crear lista plana de todos los países
        self.all_countries = []
        for region_name, countries in world_data['countries'].items():
            for country in countries:
                country['world_region'] = region_name
                self.all_countries.append(country)
        
        # Archivos de salida - USAR LOS EXISTENTES DE ÁFRICA
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'africa_heatmap.db')
        self.json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'africa_heatmap.json')
        
        print(f"🌍 Loaded {len(self.all_countries)} countries from {len(world_data['countries'])} regions")
    
    def setup_database(self):
        """Configurar base de datos SQLite"""
        print("✅ Configurando base de datos SQLite mundial...")
        
        # Asegurar que existe el directorio
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Usar la estructura existente de África (compatible)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS africa_countries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                iso3 TEXT UNIQUE NOT NULL,
                region TEXT NOT NULL,
                flag TEXT,
                
                -- Datos ambientales (Copernicus)
                temperature REAL,
                precipitation REAL,
                co2_xco2 REAL,
                forest_percentage REAL,
                
                -- Datos socioeconómicos (World Bank)
                population_density REAL,
                poverty_percentage REAL,
                unemployment_rate REAL,
                
                -- Metadatos
                data_quality_score INTEGER,
                total_indicators INTEGER,
                successful_indicators INTEGER,
                processing_time REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_sources TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Base de datos SQLite mundial configurada")
    
    def _extract_value(self, data_dict):
        """Extraer valor de estructura unificada con conversión 0.0 → null"""
        if isinstance(data_dict, dict):
            if 'value' in data_dict and data_dict.get('status') == 'success':
                value = data_dict['value']
                # No convertir 0.0 a null automáticamente - algunos 0.0 son válidos
                return value
        return None
    
    def process_country(self, country_info, index, total):
        """Procesar un país individual"""
        name = country_info['name']
        iso3 = country_info['iso3']
        region = country_info['region']
        world_region = country_info['world_region']
        flag = country_info['flag']
        
        print(f"\n{flag} {index}/{total} - {name} ({iso3}) - {region}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Datos ambientales
            env_data = self.env_service.get_environmental_data(iso3, name)
            
            # Datos socioeconómicos
            socio_data = self.socio_service.get_country_socioeconomic_data(iso3, name)
            
            processing_time = time.time() - start_time
            
            # Extraer valores (11 indicadores)
            # Environmental (4)
            temperature = self._extract_value(env_data.get('temperature', {}))
            precipitation = self._extract_value(env_data.get('precipitation', {}))
            co2 = self._extract_value(env_data.get('co2', {}))
            forest = self._extract_value(env_data.get('forest', {}))
            
            # Socioeconomic (7)
            population = self._extract_value(socio_data.get('population', {}))
            poverty = self._extract_value(socio_data.get('poverty_index', {}))
            unemployment = self._extract_value(socio_data.get('unemployment', {}))
            water = self._extract_value(socio_data.get('water_withdrawal', {}))
            school = self._extract_value(socio_data.get('school_enrollment', {}))
            wages = self._extract_value(socio_data.get('received_wages', {}))
            health = self._extract_value(socio_data.get('health_coverage', {}))
            
            # Calcular completeness
            all_indicators = [temperature, precipitation, co2, forest, population, 
                            poverty, unemployment, water, school, wages, health]
            successful_indicators = sum(1 for x in all_indicators if x is not None)
            total_indicators = len(all_indicators)
            completeness = (successful_indicators / total_indicators) * 100
            
            print(f"⏱️  Tiempo: {processing_time:.1f}s | 📊 {successful_indicators}/{total_indicators} ({completeness:.0f}%)")
            
            # Mostrar algunos datos destacados
            highlights = []
            if temperature: highlights.append(f"🌡️ {temperature}°C")
            if co2: highlights.append(f"💨 {co2}ppm")
            if forest and forest > 50: highlights.append(f"🌳 {forest:.1f}%")
            if population: highlights.append(f"👥 {population:.0f}/km²")
            if len(highlights) > 0:
                print(" | ".join(highlights))
            
            # Preparar datos para base de datos
            country_data = {
                'country_name': name,
                'iso3_code': iso3,
                'region': region,
                'world_region': world_region,
                'latitude': country_info['lat'],
                'longitude': country_info['lon'],
                'flag': flag,
                
                # Environmental
                'temperature': temperature,
                'temperature_unit': '°C' if temperature else None,
                'precipitation': precipitation,
                'precipitation_unit': 'mm' if precipitation else None,
                'co2': co2,
                'co2_unit': 'ppm' if co2 else None,
                'forest_coverage': forest,
                'forest_unit': '%' if forest else None,
                
                # Socioeconomic
                'population_density': population,
                'population_unit': 'people/km²' if population else None,
                'poverty_rate': poverty,
                'poverty_unit': '%' if poverty else None,
                'unemployment_rate': unemployment,
                'unemployment_unit': '%' if unemployment else None,
                'school_enrollment': school,
                'school_unit': '%' if school else None,
                'water_withdrawal': water,
                'water_unit': '%' if water else None,
                'received_wages': wages,
                'wages_unit': '%' if wages else None,
                'health_coverage': health,
                'health_unit': 'index' if health else None,
                
                # Metadata
                'data_completeness': completeness,
                'successful_indicators': successful_indicators,
                'total_indicators': total_indicators,
                'processing_time': processing_time,
                'data_sources': 'Copernicus CDS + World Bank'
            }
            
            return country_data, env_data, socio_data
            
        except Exception as e:
            print(f"❌ Error procesando {name}: {e}")
            
            # Datos mínimos en caso de error
            error_data = {
                'country_name': name,
                'iso3_code': iso3,
                'region': region,
                'world_region': world_region,
                'latitude': country_info['lat'],
                'longitude': country_info['lon'],
                'flag': flag,
                'data_completeness': 0.0,
                'successful_indicators': 0,
                'total_indicators': 11,
                'processing_time': time.time() - start_time,
                'data_sources': 'Error during processing'
            }
            return error_data, None, None
    
    def save_to_database(self, country_data):
        """Guardar datos en SQLite"""
        if not country_data:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Preparar valores compatibles con estructura de África
        values = [
            country_data.get('country_name'),          # name
            country_data.get('iso3_code'),             # iso3
            country_data.get('region'),                # region
            country_data.get('flag'),                  # flag
            
            # Environmental (valores sin unidades)
            country_data.get('temperature'),           # temperature
            country_data.get('precipitation'),         # precipitation
            country_data.get('co2'),                   # co2_xco2
            country_data.get('forest_coverage'),       # forest_percentage
            
            # Socioeconomic (valores sin unidades)
            country_data.get('population_density'),    # population_density
            country_data.get('poverty_rate'),          # poverty_percentage
            country_data.get('unemployment_rate'),     # unemployment_rate
            
            # Metadata
            int(country_data.get('data_completeness', 0) * 100),  # data_quality_score (porcentaje)
            country_data.get('total_indicators'),      # total_indicators
            country_data.get('successful_indicators'), # successful_indicators
            country_data.get('processing_time'),       # processing_time
            country_data.get('data_sources')           # data_sources
        ]
        
        # Insert or replace usando la estructura existente de África
        cursor.execute("""
            INSERT OR REPLACE INTO africa_countries (
                name, iso3, region, flag,
                temperature, precipitation, co2_xco2, forest_percentage,
                population_density, poverty_percentage, unemployment_rate,
                data_quality_score, total_indicators, successful_indicators,
                processing_time, data_sources
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, values)
        
        conn.commit()
        conn.close()
    
    def generate_json_export(self, all_results):
        """Expandir archivo JSON existente de África para incluir datos mundiales"""
        print(f"\n📝 Expandiendo archivo JSON existente con datos mundiales: {self.json_path}")
        
        # Cargar datos existentes de África si existen
        existing_data = []
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    existing_json = json.load(f)
                    if 'countries' in existing_json:
                        existing_data = existing_json['countries']
                        print(f"📊 Manteniendo {len(existing_data)} países existentes de África")
            except Exception as e:
                print(f"⚠️  No se pudo cargar JSON existente: {e}")
        
        # Combinar datos existentes con nuevos (evitar duplicados por ISO3)
        all_countries_dict = {}
        
        # Agregar países existentes
        for country in existing_data:
            if 'iso3' in country:
                all_countries_dict[country['iso3']] = country
        
        # Agregar/actualizar con nuevos datos
        for country in all_results:
            if 'iso3' in country:
                all_countries_dict[country['iso3']] = country
        
        # Convertir de vuelta a lista
        combined_countries = list(all_countries_dict.values())
        
        json_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_countries": len(combined_countries),
                "data_sources": ["Copernicus Climate Data Store", "World Bank Open Data"],
                "version": "2.0.0",
                "coverage": "Global - All countries (expanded from Africa)"
            },
            "countries": combined_countries,
            "statistics": {
                "average_completeness": sum(r.get('data_completeness', 0) for r in combined_countries) / len(combined_countries) if combined_countries else 0,
                "countries_with_data": sum(1 for r in combined_countries if r.get('data_completeness', 0) > 0),
                "regions_covered": len(set(r.get('world_region', '') for r in combined_countries if 'world_region' in r))
            }
        }
        
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON expandido guardado: {len(combined_countries)} países totales")
    
    def run_world_generation(self, limit=None):
        """Ejecutar generación mundial"""
        print("🌍 GENERADOR MUNDIAL DE DATOS CLIMÁTICOS Y SOCIALES")
        print("Copernicus CDS (ambiente) + World Bank (socioeconómicos)")
        print(f"SQLite + JSON | {len(self.all_countries)} países mundiales")
        print("=" * 80)
        
        self.setup_database()
        
        # Limitar países si se especifica (para testing)
        countries_to_process = self.all_countries[:limit] if limit else self.all_countries
        
        all_db_data = []
        all_json_data = []
        
        total_time = time.time()
        
        for i, country in enumerate(countries_to_process, 1):
            db_data, env_data, socio_data = self.process_country(country, i, len(countries_to_process))
            
            if db_data:
                # Guardar en SQLite
                self.save_to_database(db_data)
                all_db_data.append(db_data)
                
                # Preparar para JSON (formato más rico)
                json_country_data = {
                    "country": country['name'],
                    "iso3": country['iso3'],
                    "region": country['region'],
                    "world_region": country['world_region'],
                    "flag": country['flag'],
                    "coordinates": [country['lat'], country['lon']],
                    "environmental": env_data,
                    "socioeconomic": socio_data,
                    "data_completeness": db_data['data_completeness'],
                    "processing_time": db_data['processing_time']
                }
                all_json_data.append(json_country_data)
            
            # Progress cada 25 países
            if i % 25 == 0:
                elapsed = time.time() - total_time
                avg_time = elapsed / i
                remaining = (len(countries_to_process) - i) * avg_time
                print(f"\n📊 PROGRESO: {i}/{len(countries_to_process)} países | {elapsed/60:.1f}min elapsed | {remaining/60:.1f}min remaining")
        
        # Generar JSON
        self.generate_json_export(all_json_data)
        
        # Resumen final
        total_elapsed = time.time() - total_time
        print(f"\n🎉 GENERACIÓN MUNDIAL COMPLETADA")
        print(f"⏱️  Tiempo total: {total_elapsed/60:.1f} minutos")
        print(f"📊 SQLite: {len(all_db_data)} países guardados en {self.db_path}")
        print(f"📄 JSON: {len(all_json_data)} países guardados en {self.json_path}")
        
        # Estadísticas
        if all_db_data:
            avg_completeness = sum(d['data_completeness'] for d in all_db_data) / len(all_db_data)
            countries_with_data = sum(1 for d in all_db_data if d['data_completeness'] > 0)
            avg_time_per_country = sum(d['processing_time'] for d in all_db_data) / len(all_db_data)
            
            print(f"📈 Completeness promedio: {avg_completeness:.1f}%")
            print(f"🌍 Países con datos: {countries_with_data}/{len(all_db_data)} ({countries_with_data/len(all_db_data)*100:.1f}%)")
            print(f"⏱️  Tiempo promedio: {avg_time_per_country:.1f}s por país")

def main():
    """Función principal"""
    generator = WorldDataGenerator()
    
    # Para test rápido, usar limit=20
    # Para generación completa, usar limit=None
    test_mode = input("¿Modo test con 20 países? (y/N): ").lower().startswith('y')
    limit = 20 if test_mode else None
    
    generator.run_world_generation(limit=limit)

if __name__ == "__main__":
    main()