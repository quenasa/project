#!/usr/bin/env python3
"""
Integration test script for the Climate and Social Justice Map API
Tests all endpoints with mock data to verify functionality

Run this script to verify all endpoints are working correctly:
    python tests/test_integration.py
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
        assert response.status_code == 200

        # Test 2: Health check
        print("\n📍 Test 2: Health Check")
        response = requests.get(f"{BASE_URL}/api/health")
        print_response("GET /api/health", response)
        assert response.status_code == 200

        # Test 3: Environmental data (should be not implemented)
        print("\n📍 Test 3: Environmental Data Endpoint")
        response = requests.get(f"{BASE_URL}/api/environmental")
        print_response("GET /api/environmental", response)
        assert response.status_code == 501  # Not Implemented

        # Test 4: Socioeconomic data (should be not implemented)
        print("\n📍 Test 4: Socioeconomic Data Endpoint")
        response = requests.get(f"{BASE_URL}/api/socioeconomic")
        print_response("GET /api/socioeconomic", response)
        assert response.status_code == 501  # Not Implemented

        # Test 5: Democratic data (should be not implemented)
        print("\n📍 Test 5: Democratic Data Endpoint")
        response = requests.get(f"{BASE_URL}/api/democratic")
        print_response("GET /api/democratic", response)
        assert response.status_code == 501  # Not Implemented

        # Test 6: Vulnerability Index (should be not implemented)
        print("\n📍 Test 6: Vulnerability Index (IVSA)")
        response = requests.get(f"{BASE_URL}/api/vulnerability")
        print_response("GET /api/vulnerability", response)
        assert response.status_code == 501  # Not Implemented

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
        assert response.status_code == 201

        # Test 8: Get all reports
        print("\n📍 Test 8: Get All Reports")
        response = requests.get(f"{BASE_URL}/api/reports")
        print_response("GET /api/reports", response)
        assert response.status_code == 200

        # Test 9: Filter reports by type
        print("\n📍 Test 9: Filter Reports by Type")
        response = requests.get(f"{BASE_URL}/api/reports?type=illegal_dump")
        print_response("GET /api/reports?type=illegal_dump", response)
        assert response.status_code == 200

        # Test 10: Get specific report
        print("\n📍 Test 10: Get Specific Report")
        response = requests.get(f"{BASE_URL}/api/reports/1")
        print_response("GET /api/reports/1", response)
        assert response.status_code == 200

        # Test 11: Update report status
        print("\n📍 Test 11: Update Report Status")
        response = requests.put(
            f"{BASE_URL}/api/reports/1",
            json={"status": "verified"},
            headers={"Content-Type": "application/json"}
        )
        print_response("PUT /api/reports/1", response)
        assert response.status_code == 200

        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)
        print("\nNOTE: Environmental, Socioeconomic, Democratic, and Vulnerability")
        print("endpoints are not yet implemented (waiting for external API integration)")
        print("They correctly return 501 (Not Implemented) status")

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
        sys.exit(1)


if __name__ == "__main__":
    test_api()
