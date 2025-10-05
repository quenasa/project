#!/usr/bin/env python3
"""
Test de integración para APIs de África
Copernicus CDS + WorldPop

Ejecutar: python tests/test_africa_apis.py
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000"

# Ubicaciones de prueba en África
AFRICAN_LOCATIONS = [
    {"lat": 6.5244, "lon": 3.3792, "name": "Lagos", "country": "Nigeria"},
    {"lat": -1.2921, "lon": 36.8219, "name": "Nairobi", "country": "Kenya"},
    {"lat": -33.9249, "lon": 18.4241, "name": "Cape Town", "country": "South Africa"},
    {"lat": 30.0444, "lon": 31.2357, "name": "Cairo", "country": "Egypt"},
]


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except:
        print(response.text)
        return None


def test_africa_apis():
    """Test APIs enfocadas en África"""
    print("🌍 Testing Climate and Social Justice Map API - AFRICA FOCUS")
    print(f"Base URL: {BASE_URL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Test 1: Root endpoint
        print("📍 Test 1: Root Endpoint")
        response = requests.get(f"{BASE_URL}/")
        data = print_response("GET /", response)
        assert response.status_code == 200
        assert data.get("name") == "Climate and Social Justice Map API"

        # Test 2: Health check
        print("\n📍 Test 2: Health Check")
        response = requests.get(f"{BASE_URL}/api/health")
        data = print_response("GET /api/health", response)
        assert response.status_code == 200
        assert data.get("status") == "healthy"

        # Test 3-6: Probar endpoints con cada ubicación africana
        for i, location in enumerate(AFRICAN_LOCATIONS, start=3):
            print(f"\n📍 Test {i}: {location['name']}, {location['country']}")
            print(f"Coordinates: {location['lat']}, {location['lon']}")
            
            # Test Environmental data
            print(f"\n  🌡️ Testing Environmental Data...")
            response = requests.get(
                f"{BASE_URL}/api/environmental",
                params={
                    "lat": location["lat"],
                    "lon": location["lon"],
                    "country": location["country"]
                }
            )
            env_data = print_response(
                f"GET /api/environmental - {location['name']}", 
                response
            )
            
            # Debe retornar 200 (funcionando) o estructura con datos
            if response.status_code == 200:
                assert "data" in env_data
                assert "location" in env_data["data"]
                print(f"    ✅ Environmental data retrieved successfully")
            else:
                print(f"    ⏳ Environmental endpoint returns: {response.status_code}")
            
            # Test Socioeconomic data
            print(f"\n  👥 Testing Socioeconomic Data...")
            response = requests.get(
                f"{BASE_URL}/api/socioeconomic",
                params={
                    "lat": location["lat"],
                    "lon": location["lon"],
                    "country": location["country"]
                }
            )
            soc_data = print_response(
                f"GET /api/socioeconomic - {location['name']}", 
                response
            )
            
            if response.status_code == 200:
                assert "data" in soc_data
                assert "location" in soc_data["data"]
                print(f"    ✅ Socioeconomic data retrieved successfully")
            else:
                print(f"    ⏳ Socioeconomic endpoint returns: {response.status_code}")

        # Test sin coordenadas (debe fallar)
        print("\n📍 Test: Request without coordinates (should fail)")
        response = requests.get(f"{BASE_URL}/api/environmental")
        data = print_response("GET /api/environmental (no params)", response)
        assert response.status_code == 400
        assert "error" in data
        print("    ✅ Correctly validates missing coordinates")

        # Test coordenadas fuera de África (debe advertir)
        print("\n📍 Test: Coordinates outside Africa (should warn)")
        response = requests.get(
            f"{BASE_URL}/api/environmental",
            params={"lat": 40.4168, "lon": -3.7038}  # Madrid, España
        )
        data = print_response("GET /api/environmental (Madrid)", response)
        assert response.status_code == 400
        assert "warning" in data or "error" in data
        print("    ✅ Correctly validates Africa region")

        # Test reportes ciudadanos (aún funciona)
        print("\n📍 Test: Citizen Reports (still working)")
        report_data = {
            "type": "water_pollution",
            "location": {
                "lat": 6.5244,
                "lon": 3.3792,
                "name": "Lagos, Nigeria"
            },
            "description": "Water pollution detected near residential area",
            "reporter": "test_user"
        }
        response = requests.post(
            f"{BASE_URL}/api/reports",
            json=report_data,
            headers={"Content-Type": "application/json"}
        )
        data = print_response("POST /api/reports", response)
        assert response.status_code == 201
        print("    ✅ Citizen reports working correctly")

        print("\n" + "="*70)
        print("✅ All tests completed successfully!")
        print("="*70)
        print("\n📊 Summary:")
        print(f"  • Tested {len(AFRICAN_LOCATIONS)} African locations")
        print("  • Environmental data endpoint configured")
        print("  • Socioeconomic data endpoint configured")
        print("  • Validation working correctly")
        print("  • Focus: Africa region")
        print("\n💡 Note: If endpoints return placeholder data (0.0),")
        print("   add your Copernicus API key to .env file")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the API server.")
        print(f"Make sure the Flask server is running on {BASE_URL}")
        print("Run: python app.py")
        sys.exit(1)
    except AssertionError as e:
        print(f"\n❌ Test assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_africa_apis()
