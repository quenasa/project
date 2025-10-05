#!/usr/bin/env python3
"""
DEBUG - Verificar por qué la densidad de población no se muestra
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.socioeconomic_service import SocioeconomicService

def debug_population_mapping():
    print("🔍 DEBUG - DENSIDAD DE POBLACIÓN")
    print("="*50)
    
    socio_service = SocioeconomicService()
    
    # Test con Gabon (país que muestra datos socioeconómicos)
    socio_data = socio_service.get_country_socioeconomic_data("GAB", "Gabon")
    
    print("🏛️ ESTRUCTURA COMPLETA:")
    for key, value in socio_data.items():
        if isinstance(value, dict) and 'value' in value:
            print(f"  {key}: {value['value']} {value.get('unit', '')} (status: {value.get('status', 'unknown')})")
        else:
            print(f"  {key}: {value}")
    
    print("\n🔍 POBLACIÓN ESPECÍFICA:")
    population_data = socio_data.get('population', {})
    if population_data:
        print(f"  population object: {population_data}")
        print(f"  value: {population_data.get('value', 'NOT FOUND')}")
        print(f"  status: {population_data.get('status', 'NOT FOUND')}")
    else:
        print("  ❌ No population key found")
    
    # Test función de limpieza del test
    def clean_value_with_status(data_obj, value_key, indicator_name):
        status = data_obj.get('status', 'unknown')
        value = data_obj.get(value_key, None)
        
        if status in ['error', 'no_data', 'failed'] or value is None:
            return "N/A"
        return value
    
    population_clean = clean_value_with_status(population_data, 'value', 'population')
    print(f"\n✅ RESULTADO LIMPIO: {population_clean}")

if __name__ == "__main__":
    debug_population_mapping()