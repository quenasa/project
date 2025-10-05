#!/usr/bin/env python3
"""
DEBUG - Ver exactamente qué datos se están obteniendo
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.environmental_service import EnvironmentalService
from services.socioeconomic_service import SocioeconomicService
import json

def debug_complete_data():
    print("🔍 DEBUG - DATOS COMPLETOS EGYPT")
    print("="*50)
    
    env_service = EnvironmentalService()
    socio_service = SocioeconomicService()
    
    # Test con Egypt
    print("🌿 ENVIRONMENTAL DATA:")
    env_data = env_service.get_environmental_data("EGY", "Egypt")
    
    for key, value in env_data.items():
        if isinstance(value, dict):
            status = value.get('status', 'unknown')
            val = value.get('value', 'NO VALUE FIELD')
            print(f"  {key}: value={val}, status={status}")
        else:
            print(f"  {key}: {value}")
    
    print("\n🏛️ SOCIOECONOMIC DATA:")
    socio_data = socio_service.get_country_socioeconomic_data("EGY", "Egypt")
    
    for key, value in socio_data.items():
        if isinstance(value, dict):
            status = value.get('status', 'unknown')
            val = value.get('value', 'NO VALUE FIELD')
            print(f"  {key}: value={val}, status={status}")
        else:
            print(f"  {key}: {value}")
    
    # Test extract_value function
    print("\n🧮 TESTING EXTRACT_VALUE:")
    def extract_value(data_obj):
        if isinstance(data_obj, dict):
            if 'value' in data_obj and data_obj.get('status') == 'success':
                return data_obj['value']
        return None
    
    # Test environmental
    temperature = extract_value(env_data.get('temperature', {}))
    precipitation = extract_value(env_data.get('precipitation', {}))
    co2 = extract_value(env_data.get('co2', {}))
    forest = extract_value(env_data.get('forest', {}))
    
    print(f"  temperature: {temperature}")
    print(f"  precipitation: {precipitation}")
    print(f"  co2: {co2}")
    print(f"  forest: {forest}")
    
    # Test socioeconomic
    population = extract_value(socio_data.get('population', {}))
    poverty = extract_value(socio_data.get('poverty_index', {}))
    unemployment = extract_value(socio_data.get('unemployment', {}))
    school = extract_value(socio_data.get('school_enrollment', {}))
    
    print(f"  population: {population}")
    print(f"  poverty: {poverty}")
    print(f"  unemployment: {unemployment}")
    print(f"  school: {school}")
    
    # Count available
    all_indicators = [temperature, precipitation, co2, forest, population, 
                     poverty, unemployment, school]
    available_count = sum(1 for x in all_indicators if x is not None)
    
    print(f"\n✅ AVAILABLE: {available_count}/{len(all_indicators)} ({available_count/len(all_indicators)*100:.0f}%)")

if __name__ == "__main__":
    debug_complete_data()