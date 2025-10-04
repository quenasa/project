#!/usr/bin/env python3
"""
Simple test script for the Climate and Social Justice Map API
Run this script to verify all endpoints are working correctly.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_api():
    """Test all API endpoints"""
    print("🌍 Testing Climate and Social Justice Map API")
    print(f"Base URL: {BASE_URL}\n")

    try:
        # Test 1: Root endpoint
        print("📍 Test 1: Root Endpoint")
        response = requests.get(f"{BASE_URL}/")
        print_response("GET /", response)

        # Test 2: Health check
        print("\n📍 Test 2: Health Check")
        response = requests.get(f"{BASE_URL}/api/health")
        print_response("GET /api/health", response)

        # Test 3: Environmental data
        print("\n📍 Test 3: Environmental Data")
        response = requests.get(f"{BASE_URL}/api/environmental")
        print_response("GET /api/environmental", response)

        # Test 4: Socioeconomic data
        print("\n📍 Test 4: Socioeconomic Data")
        response = requests.get(f"{BASE_URL}/api/socioeconomic")
        print_response("GET /api/socioeconomic", response)

        # Test 5: Democratic data
        print("\n📍 Test 5: Democratic Data")
        response = requests.get(f"{BASE_URL}/api/democratic")
        print_response("GET /api/democratic", response)

        # Test 6: Vulnerability Index
        print("\n📍 Test 6: Vulnerability Index (IVSA)")
        response = requests.get(f"{BASE_URL}/api/vulnerability")
        print_response("GET /api/vulnerability", response)

        # Test 7: Submit citizen report
        print("\n📍 Test 7: Submit Citizen Report")
        report_data = {
            "type": "illegal_dump",
            "location": {
                "lat": 40.416775,
                "lon": -3.703790,
                "name": "Madrid Centro"
            },
            "description": "Illegal waste dump found near residential area",
            "reporter": "citizen_test"
        }
        response = requests.post(
            f"{BASE_URL}/api/reports",
            json=report_data,
            headers={"Content-Type": "application/json"}
        )
        print_response("POST /api/reports", response)

        # Test 8: Get all reports
        print("\n📍 Test 8: Get All Reports")
        response = requests.get(f"{BASE_URL}/api/reports")
        print_response("GET /api/reports", response)

        # Test 9: Filter environmental data by location
        print("\n📍 Test 9: Filter by Location")
        response = requests.get(f"{BASE_URL}/api/environmental?location=Madrid")
        print_response("GET /api/environmental?location=Madrid", response)

        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the API server.")
        print(f"Make sure the Flask server is running on {BASE_URL}")
        print("Run: python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_api()
