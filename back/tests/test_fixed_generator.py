#!/usr/bin/env python3
"""
TEST del generador corregido con Egypt
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.generate_africa_data import AfricaDataGenerator

def test_fixed_generator():
    print("🔧 TEST DEL GENERADOR CORREGIDO")
    print("="*50)
    
    generator = AfricaDataGenerator()
    
    # Test con Egypt
    country_info = {'name': 'Egypt', 'iso3': 'EGY', 'region': 'North Africa', 'flag': '🇪🇬'}
    
    print("🌍 Testing Egypt...")
    
    # Simular el procesamiento
    try:
        env_data = generator.env_service.get_environmental_data("EGY", "Egypt")
        socio_data = generator.socio_service.get_country_socioeconomic_data("EGY", "Egypt")
        
        # Test de extracción
        temperature = generator._extract_value(env_data.get('temperature', {}))
        precipitation = generator._extract_value(env_data.get('precipitation', {}))
        co2 = generator._extract_value(env_data.get('co2', {}))
        forest = generator._extract_value(env_data.get('forest', {}))
        
        population = generator._extract_value(socio_data.get('population', {}))
        poverty = generator._extract_value(socio_data.get('poverty_index', {}))
        unemployment = generator._extract_value(socio_data.get('unemployment', {}))
        water = generator._extract_value(socio_data.get('water_withdrawal', {}))
        school = generator._extract_value(socio_data.get('school_enrollment', {}))
        wages = generator._extract_value(socio_data.get('received_wages', {}))
        health = generator._extract_value(socio_data.get('health_coverage', {}))
        
        # Contar
        values = [temperature, precipitation, co2, forest, population, 
                 poverty, unemployment, water, school, wages, health]
        successful = sum(1 for v in values if v is not None)
        total = len(values)
        
        print(f"📊 RESULTADO: {successful}/{total} ({successful/total*100:.0f}%)")
        print(f"🌡️  Temperature: {temperature}")
        print(f"🌧️  Precipitation: {precipitation}")
        print(f"💨 CO2: {co2}")
        print(f"🌳 Forest: {forest}")
        print(f"👥 Population: {population}")
        print(f"💰 Poverty: {poverty}")
        print(f"📊 Unemployment: {unemployment}")
        print(f"💧 Water: {water}")
        print(f"🎓 School: {school}")
        print(f"💵 Wages: {wages}")
        print(f"🏥 Health: {health}")
        
        if successful > 7:
            print("\n✅ ¡GENERADOR CORREGIDO! Ahora cuenta correctamente")
        else:
            print("\n❌ Aún hay problemas")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_fixed_generator()