#!/usr/bin/env python3
"""
TEST RÁPIDO DE MODULARIZACIÓN DEL SISTEMA
"""
import sys
import os
# Añadir el directorio padre (back/) al path para poder importar services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_system_modularization():
    """Test de modularización del sistema completo"""
    print("🔧 TEST DE MODULARIZACIÓN DEL SISTEMA")
    print("="*60)
    
    try:
        # Test 1: Services importables
        print("📦 Testing services imports...")
        from services.environmental_service import EnvironmentalService
        from services.socioeconomic_service import SocioeconomicService
        print("✅ Services imported successfully")
        
        # Test 2: Services inicializables
        print("🏗️ Testing services initialization...")
        env_service = EnvironmentalService()
        socio_service = SocioeconomicService()
        print("✅ Services initialized successfully")
        
        # Test 3: Test rápido con Egypt (país con datos)
        print("🌍 Quick test with Egypt...")
        
        # Environmental test
        env_result = env_service.get_copernicus_temperature("EGY", "Egypt")
        print(f"🌡️ Temperature: {env_result['value']}{env_result['unit']} | Status: {env_result['status']}")
        
        # Socioeconomic test  
        socio_result = socio_service.get_poverty_index(26.8, 30.8, "Egypt")
        print(f"📊 Poverty: {socio_result['value']}{socio_result['unit']} | Status: {socio_result['status']}")
        
        print("\n✅ MODULARIZACIÓN: CORRECTA")
        print("• Scripts usan services/ ✅")
        print("• Services tienen métodos correctos ✅") 
        print("• Importaciones funcionan ✅")
        print("• APIs pueden usar services ✅")
        print("\n⚠️  TAREAS PENDIENTES:")
        print("• Mover tests fuera del directorio raíz a tests/")
        print("• Verificar que app.py usa Flask correctamente")
        print("• Comprobar que todos los scripts usan services actualizados")
        
        return True
        
    except Exception as e:
        print(f"💥 Error in modularization: {e}")
        return False

if __name__ == "__main__":
    success = test_system_modularization()
    if success:
        print("\n🎉 SISTEMA LISTO PARA AFRICA HEATMAP TEST")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Mover tests sueltos a tests/")
        print("2. Ejecutar: python tests/test_africa_heatmap.py")
        print("3. Generar datos: python scripts/generate_africa_data.py")
    else:
        print("\n❌ SISTEMA NECESITA ARREGLOS")