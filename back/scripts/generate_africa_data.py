"""
🌍 SCRIPT GENERADOR DE DATOS ÁFRICA - SQLite + JSON
==================================================

Script principal que:
✅ Procesa TODOS los países de África 
✅ Guarda en SQLite (base de datos)
✅ Guarda en JSON (para frontend)
✅ Copernicus: CO2, temperatura, precipitación, forest
✅ World Bank: socioeconómicos
✅ 0.0 → null automático

Para ejecutar: python scripts/generate_africa_data.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
import json
import time
from datetime import datetime
from services.environmental_service import EnvironmentalService
from services.socioeconomic_service import SocioeconomicService

class AfricaDataGenerator:
    def __init__(self):
        """Iniciailizar generador de datos de África"""
        self.env_service = EnvironmentalService()  # Todo Copernicus
        self.socio_service = SocioeconomicService()  # World Bank
        
        # 🌍 Cargar países africanos desde JSON global
        with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'world_countries.json'), 'r', encoding='utf-8') as f:
            world_data = json.load(f)
        
        # Extraer solo países africanos
        self.african_countries = world_data['countries']['africa']
        print(f"� Loaded {len(self.african_countries)} African countries from world_countries.json")
        
        # Archivos de salida
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'africa_heatmap.db')
        self.json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'africa_heatmap.json')
        
        # Crear directorio data si no existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def setup_database(self):
        """🗄️ Crear estructura de base de datos SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla principal de países
        cursor.execute('''
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
                last_updated TIMESTAMP,
                data_sources TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de datos SQLite configurada")
    
    def process_all_countries(self):
        """🌍 Procesar todos los países de África"""
        print("🌍 GENERANDO DATOS PARA TODOS LOS PAÍSES DE ÁFRICA")
        print("=" * 60)
        
        all_results = []
        total_start = time.time()
        
        for i, country in enumerate(self.african_countries, 1):
            name = country['name']
            iso3 = country['iso3']
            region = country['region']
            flag = country['flag']
            
            print(f"\n{flag} {i:2d}/54 - {name} ({iso3}) - {region}")
            print("-" * 45)
            
            start_time = time.time()
            
            try:
                # 🛰️ Datos ambientales (Copernicus)
                env_data = self.env_service.get_environmental_data(iso3, name)
                
                # 🏦 Datos socioeconómicos (World Bank)
                socio_data = self.socio_service.get_country_socioeconomic_data(iso3, name)
                
                processing_time = time.time() - start_time
                
                # Extraer valores de estructura unificada con 0.0 → null
                # Environmental (4 indicadores)
                temperature = self._extract_value(env_data.get('temperature', {}))
                precipitation = self._extract_value(env_data.get('precipitation', {}))
                co2_xco2 = self._extract_value(env_data.get('co2', {}))
                forest_percentage = self._extract_value(env_data.get('forest', {}))
                
                # Socioeconomic (7 indicadores)
                population_density = self._extract_value(socio_data.get('population', {}))
                poverty_percentage = self._extract_value(socio_data.get('poverty_index', {}))
                unemployment_rate = self._extract_value(socio_data.get('unemployment', {}))
                water_withdrawal = self._extract_value(socio_data.get('water_withdrawal', {}))
                school_enrollment = self._extract_value(socio_data.get('school_enrollment', {}))
                received_wages = self._extract_value(socio_data.get('received_wages', {}))
                health_coverage = self._extract_value(socio_data.get('health_coverage', {}))
                
                # Calcular calidad de datos (11 indicadores totales)
                values = [temperature, precipitation, co2_xco2, forest_percentage, 
                         population_density, poverty_percentage, unemployment_rate,
                         water_withdrawal, school_enrollment, received_wages, health_coverage]
                successful_indicators = sum(1 for v in values if v is not None)
                total_indicators = len(values)  # 11 indicadores
                data_quality_score = int((successful_indicators / total_indicators) * 100)
                
                # Crear resultado
                result = {
                    'name': name,
                    'iso3': iso3,
                    'region': region,
                    'flag': flag,
                    # Environmental (4)
                    'temperature': temperature,
                    'precipitation': precipitation,
                    'co2_xco2': co2_xco2,
                    'forest_percentage': forest_percentage,
                    # Socioeconomic (7)
                    'population_density': population_density,
                    'poverty_percentage': poverty_percentage,
                    'unemployment_rate': unemployment_rate,
                    'water_withdrawal': water_withdrawal,
                    'school_enrollment': school_enrollment,
                    'received_wages': received_wages,
                    'health_coverage': health_coverage,
                    # Metadata
                    'data_quality_score': data_quality_score,
                    'total_indicators': total_indicators,
                    'successful_indicators': successful_indicators,
                    'processing_time': processing_time,
                    'last_updated': datetime.now().isoformat(),
                    'data_sources': 'Copernicus CDS (ambiente) + World Bank (socioeconómicos)'
                }
                
                all_results.append(result)
                
                # Mostrar progreso
                print(f"⏱️  {processing_time:.1f}s | 📊 {successful_indicators}/{total_indicators} ({data_quality_score}%)")
                
                # Mostrar algunos datos clave
                if temperature: print(f"🌡️  {temperature}°C", end=" ")
                if co2_xco2: print(f"💨 {co2_xco2}ppm", end=" ")
                if forest_percentage: print(f"🌳 {forest_percentage:.1f}%", end=" ")
                if population_density: print(f"👥 {population_density:.0f}/km²")
                else: print()
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)[:40]}...")
                # Agregar resultado con error
                result = {
                    'name': name,
                    'iso3': iso3,
                    'region': region,
                    'flag': flag,
                    'data_quality_score': 0,
                    'successful_indicators': 0,
                    'total_indicators': 11,
                    'processing_time': 0,
                    'error': str(e),
                    'last_updated': datetime.now().isoformat()
                }
                all_results.append(result)
        
        total_time = time.time() - total_start
        
        # Guardar resultados
        self.save_to_sqlite(all_results)
        self.save_to_json(all_results)
        
        # Mostrar resumen
        self.show_summary(all_results, total_time)
        
        return all_results
    
    def _extract_value(self, data_dict, key='value'):
        """Extraer valor de estructura unificada con conversión 0.0 → null"""
        if isinstance(data_dict, dict):
            # Nuevo formato unificado
            if 'value' in data_dict and data_dict.get('status') == 'success':
                value = data_dict['value']
                if value == 0.0:
                    return None
                return value
            # Formato legacy para compatibilidad
            elif key in data_dict:
                value = data_dict.get(key)
                if value == 0.0:
                    return None
                return value
        return None
    
    def save_to_sqlite(self, results):
        """💾 Guardar resultados en SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Limpiar tabla existente
        cursor.execute('DELETE FROM africa_countries')
        
        # Insertar nuevos datos
        for result in results:
            cursor.execute('''
                INSERT INTO africa_countries (
                    name, iso3, region, flag,
                    temperature, precipitation, co2_xco2, forest_percentage,
                    population_density, poverty_percentage, unemployment_rate,
                    data_quality_score, total_indicators, successful_indicators,
                    processing_time, last_updated, data_sources
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.get('name'), result.get('iso3'), result.get('region'), result.get('flag'),
                result.get('temperature'), result.get('precipitation'), 
                result.get('co2_xco2'), result.get('forest_percentage'),
                result.get('population_density'), result.get('poverty_percentage'), 
                result.get('unemployment_rate'),
                result.get('data_quality_score'), result.get('total_indicators'), 
                result.get('successful_indicators'),
                result.get('processing_time'), result.get('last_updated'), 
                result.get('data_sources')
            ))
        
        conn.commit()
        conn.close()
        print(f"✅ Datos guardados en SQLite: {self.db_path}")
    
    def save_to_json(self, results):
        """📄 Guardar resultados en JSON"""
        json_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_countries': len(results),
                'data_sources': ['Copernicus Climate Data Store', 'World Bank Open Data'],
                'indicators': {
                    'environmental': ['temperature', 'precipitation', 'co2_xco2', 'forest_percentage'],
                    'socioeconomic': ['population_density', 'poverty_percentage', 'unemployment_rate']
                }
            },
            'countries': results
        }
        
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Datos guardados en JSON: {self.json_path}")
    
    def show_summary(self, results, total_time):
        """📊 Mostrar resumen final"""
        print("\n" + "=" * 60)
        print("🏆 RESUMEN FINAL - GENERACIÓN DATOS ÁFRICA")
        print("=" * 60)
        
        successful_results = [r for r in results if r.get('data_quality_score', 0) > 0]
        avg_quality = sum(r.get('data_quality_score', 0) for r in successful_results) / len(successful_results) if successful_results else 0
        
        print(f"🌍 Países procesados: {len(results)}/54")
        print(f"✅ Países con datos: {len(successful_results)}")
        print(f"⏱️  Tiempo total: {total_time/60:.1f} minutos ({total_time/len(results):.1f}s promedio)")
        print(f"📊 Calidad promedio: {avg_quality:.1f}%")
        print(f"💾 SQLite: {self.db_path}")
        print(f"📄 JSON: {self.json_path}")
        
        # Top 5 países por calidad de datos
        top_countries = sorted(successful_results, key=lambda x: x.get('data_quality_score', 0), reverse=True)[:5]
        print(f"\n🏆 Top 5 países por calidad de datos:")
        for i, country in enumerate(top_countries, 1):
            print(f"   {i}. {country['flag']} {country['name']}: {country['data_quality_score']}%")

def main():
    """🚀 Función principal"""
    print("🌍 GENERADOR DE DATOS MAPA DE CALOR ÁFRICA")
    print("Copernicus (ambiente) + World Bank (socioeconómicos)")
    print("SQLite + JSON | 0.0 → null automático")
    print()
    
    generator = AfricaDataGenerator()
    generator.setup_database()
    results = generator.process_all_countries()
    
    print(f"\n🎉 ¡COMPLETADO! Datos listos para mapa de calor interactivo")

if __name__ == "__main__":
    main()