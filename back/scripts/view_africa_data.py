"""
🔍 SCRIPT VISOR DE DATOS ÁFRICA - SQLite Query Tool
==================================================

Script para consultar y visualizar los datos generados
✅ Consultas SQLite
✅ Estadísticas por región
✅ Filtros por calidad de datos
✅ Export específico

Para ejecutar: python scripts/view_africa_data.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
import json
from datetime import datetime

class AfricaDataViewer:
    def __init__(self):
        """Inicializar visor de datos"""
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'africa_heatmap.db')
        
        if not os.path.exists(self.db_path):
            print(f"❌ Base de datos no encontrada: {self.db_path}")
            print("💡 Primero ejecuta: python scripts/generate_africa_data.py")
            sys.exit(1)
    
    def show_all_countries(self):
        """📋 Mostrar todos los países"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, iso3, region, flag, data_quality_score, 
                   successful_indicators, total_indicators,
                   temperature, co2_xco2, forest_percentage
            FROM africa_countries 
            ORDER BY data_quality_score DESC, name
        ''')
        
        countries = cursor.fetchall()
        conn.close()
        
        print("🌍 TODOS LOS PAÍSES DE ÁFRICA")
        print("=" * 80)
        print(f"{'Flag':<4} {'País':<25} {'Región':<15} {'Calidad':<8} {'Temp':<6} {'CO2':<6} {'Forest':<7}")
        print("-" * 80)
        
        for country in countries:
            name, iso3, region, flag, quality, success, total, temp, co2, forest = country
            temp_str = f"{temp:.1f}°C" if temp else "---"
            co2_str = f"{co2:.0f}" if co2 else "---"
            forest_str = f"{forest:.1f}%" if forest else "---"
            
            print(f"{flag:<4} {name:<25} {region:<15} {quality}%{'':<3} {temp_str:<6} {co2_str:<6} {forest_str:<7}")
        
        print(f"\nTotal países: {len(countries)}")
    
    def show_by_region(self):
        """🗺️ Mostrar estadísticas por región"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT region, 
                   COUNT(*) as total_countries,
                   AVG(data_quality_score) as avg_quality,
                   AVG(temperature) as avg_temp,
                   AVG(co2_xco2) as avg_co2,
                   AVG(forest_percentage) as avg_forest
            FROM africa_countries 
            GROUP BY region
            ORDER BY avg_quality DESC
        ''')
        
        regions = cursor.fetchall()
        conn.close()
        
        print("\n🗺️ ESTADÍSTICAS POR REGIÓN")
        print("=" * 70)
        print(f"{'Región':<20} {'Países':<8} {'Calidad':<8} {'Temp':<8} {'CO2':<8} {'Forest'}")
        print("-" * 70)
        
        for region_data in regions:
            region, total, quality, temp, co2, forest = region_data
            quality_str = f"{quality:.1f}%" if quality else "---"
            temp_str = f"{temp:.1f}°C" if temp else "---"
            co2_str = f"{co2:.0f}ppm" if co2 else "---"
            forest_str = f"{forest:.1f}%" if forest else "---"
            
            print(f"{region:<20} {total:<8} {quality_str:<8} {temp_str:<8} {co2_str:<8} {forest_str}")
    
    def show_best_countries(self, limit=10):
        """🏆 Mostrar mejores países por calidad de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, flag, region, data_quality_score, 
                   temperature, precipitation, co2_xco2, forest_percentage,
                   population_density, unemployment_rate
            FROM africa_countries 
            WHERE data_quality_score > 0
            ORDER BY data_quality_score DESC, name
            LIMIT ?
        ''', (limit,))
        
        countries = cursor.fetchall()
        conn.close()
        
        print(f"\n🏆 TOP {limit} PAÍSES POR CALIDAD DE DATOS")
        print("=" * 90)
        
        for i, country in enumerate(countries, 1):
            name, flag, region, quality, temp, precip, co2, forest, pop_density, unemployment = country
            
            print(f"{i:2d}. {flag} {name} ({region}) - {quality}%")
            
            # Mostrar datos disponibles
            data_points = []
            if temp: data_points.append(f"🌡️{temp:.1f}°C")
            if precip: data_points.append(f"🌧️{precip:.0f}mm")
            if co2: data_points.append(f"💨{co2:.0f}ppm")
            if forest: data_points.append(f"🌳{forest:.1f}%")
            if pop_density: data_points.append(f"👥{pop_density:.0f}/km²")
            if unemployment: data_points.append(f"💼{unemployment:.1f}%")
            
            if data_points:
                print(f"    {' | '.join(data_points)}")
            print()
    
    def export_for_frontend(self, min_quality=50):
        """📊 Exportar datos para frontend (solo países con buena calidad)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, iso3, region, flag,
                   temperature, precipitation, co2_xco2, forest_percentage,
                   population_density, poverty_percentage, unemployment_rate,
                   data_quality_score
            FROM africa_countries 
            WHERE data_quality_score >= ?
            ORDER BY name
        ''', (min_quality,))
        
        countries = cursor.fetchall()
        conn.close()
        
        # Convertir a formato frontend
        frontend_data = []
        for country in countries:
            name, iso3, region, flag, temp, precip, co2, forest, pop_density, poverty, unemployment, quality = country
            
            frontend_data.append({
                'country': name,
                'iso3': iso3,
                'region': region,
                'flag': flag,
                'indicators': {
                    'temperature': temp,
                    'precipitation': precip,
                    'co2_concentration': co2,
                    'forest_coverage': forest,
                    'population_density': pop_density,
                    'poverty_rate': poverty,
                    'unemployment_rate': unemployment
                },
                'data_quality': quality
            })
        
        # Guardar archivo para frontend
        frontend_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'africa_frontend.json')
        with open(frontend_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'min_quality_threshold': min_quality,
                    'total_countries': len(frontend_data),
                    'data_sources': 'Copernicus + World Bank'
                },
                'countries': frontend_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Exportado para frontend: {len(frontend_data)} países (calidad ≥{min_quality}%)")
        print(f"💾 Archivo: {frontend_file}")
        
        return frontend_data
    
    def show_menu(self):
        """📋 Mostrar menú interactivo"""
        while True:
            print("\n" + "="*50)
            print("🔍 VISOR DE DATOS ÁFRICA - MENÚ")
            print("="*50)
            print("1. 📋 Ver todos los países")
            print("2. 🗺️  Estadísticas por región")
            print("3. 🏆 Top países por calidad")
            print("4. 📊 Exportar para frontend")
            print("5. 🚪 Salir")
            print()
            
            try:
                choice = input("Selecciona una opción (1-5): ").strip()
                
                if choice == '1':
                    self.show_all_countries()
                elif choice == '2':
                    self.show_by_region()
                elif choice == '3':
                    try:
                        limit = int(input("¿Cuántos países mostrar? (por defecto 10): ") or "10")
                        self.show_best_countries(limit)
                    except ValueError:
                        self.show_best_countries()
                elif choice == '4':
                    try:
                        min_quality = int(input("Calidad mínima % (por defecto 50): ") or "50")
                        self.export_for_frontend(min_quality)
                    except ValueError:
                        self.export_for_frontend()
                elif choice == '5':
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción no válida")
                    
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """🚀 Función principal"""
    print("🔍 VISOR DE DATOS MAPA DE CALOR ÁFRICA")
    print("Consulta SQLite | Estadísticas | Export Frontend")
    
    viewer = AfricaDataViewer()
    viewer.show_menu()

if __name__ == "__main__":
    main()