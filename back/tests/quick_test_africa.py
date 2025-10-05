#!/usr/bin/env python3
"""
TEST RÁPIDO para verificar que el test de Africa funciona correctamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.environmental_service import EnvironmentalService
from services.socioeconomic_service import SocioeconomicService

def quick_test_egypt():
    """Test rápido con Egypt usando los métodos agregados"""
    print("🌍 QUICK TEST - EGYPT CON MÉTODOS AGREGADOS")
    print("="*50)
    
    env_service = EnvironmentalService()
    socio_service = SocioeconomicService()
    
    # Usar los mismos métodos que el test de Africa
    env_data = env_service.get_environmental_data("EGY", "Egypt")
    socio_data = socio_service.get_country_socioeconomic_data("EGY", "Egypt")
    
    # Simular la lógica del test
    def clean_value_with_status(data_obj, value_key, indicator_name):
        status = data_obj.get('status', 'unknown')
        value = data_obj.get(value_key, None)
        
        if status in ['error', 'no_data', 'failed'] or value is None:
            return "N/A"
        return value
    
    # Test valores
    temperature = clean_value_with_status(env_data.get('temperature', {}), 'value', 'temperature')
    precipitation = clean_value_with_status(env_data.get('precipitation', {}), 'value', 'precipitation')
    poverty = clean_value_with_status(socio_data.get('poverty_index', {}), 'value', 'poverty')
    school = clean_value_with_status(socio_data.get('school_enrollment', {}), 'value', 'school')
    
    print(f"🌡️ Temperature: {temperature}")
    print(f"🌧️ Precipitation: {precipitation}")
    print(f"📊 Poverty: {poverty}")
    print(f"🎓 School: {school}")
    
    # Count success
    all_values = [temperature, precipitation, poverty, school]
    success_count = sum(1 for val in all_values if val != 'N/A')
    
    print(f"\n✅ Success rate: {success_count}/4 ({success_count/4*100:.0f}%)")
    
    if success_count > 0:
        print("🎉 ¡EL TEST DE AFRICA DEBERÍA FUNCIONAR!")
    else:
        print("❌ Hay problemas con los datos")

if __name__ == "__main__":
    quick_test_egypt()