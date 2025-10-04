"""
Simple test for temperature data from Copernicus
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.environmental_service import EnvironmentalService
from flask import Flask

# Create minimal Flask app for context
app = Flask(__name__)
app.config['COPERNICUS_API_KEY'] = os.getenv('COPERNICUS_API_KEY', 'c25e9fac-26a7-4096-92c5-471d68b269e5')
app.config['COPERNICUS_API_URL'] = 'https://cds.climate.copernicus.eu/api'

print("=" * 70)
print("Testing Copernicus Temperature API")
print("=" * 70)

with app.app_context():
    service = EnvironmentalService()
    
    # Test Lagos, Nigeria
    print("\n📍 Testing Lagos, Nigeria (6.5244, 3.3792)")
    print("-" * 70)
    
    result = service.get_temperature(6.5244, 3.3792)
    
    print("\n🌡️ Temperature Result:")
    print(f"  Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'success':
        print(f"  ✅ Temperature: {result.get('current')}°C")
        print(f"  ✅ Precipitation: {result.get('precipitation_mm')}mm")
        print(f"  📅 Date: {result.get('date')} ({result.get('days_old')} days old)")
        print(f"  🔥 Heat wave risk: {result.get('heat_wave_risk')}")
    elif result.get('status') == 'error':
        print(f"  ❌ Error: {result.get('error')}")
    else:
        print(f"  ⚠️ Status: {result.get('status')}")
        print(f"  Full result: {result}")
    
    print("\n" + "=" * 70)
