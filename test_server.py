#!/usr/bin/env python3
"""
Test script for the Acme Todo MCP Server
Tests both search and fetch endpoints against localhost:5004
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:5004"
BASE_URL = "https://acme-todo-gpt-mcp.ritzademo.com"

def make_request(endpoint: str, data: Dict[str, Any]) -> None:
    """Make a POST request to the specified endpoint and print results"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    print(f"\n{'='*60}")
    print(f"Testing {endpoint}")
    print(f"Request: {json.dumps(data, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure the server is running on localhost:5004")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_search_endpoint():
    """Test the search endpoint with various queries"""
    print("\n🔍 TESTING SEARCH ENDPOINT")
    
    # Test 1: Search for "development"
    make_request("/search", {"query": "development"})
    
    # Test 2: Search for "test"
    make_request("/search", {"query": "test"})
    
    # Test 3: Search for "deploy"
    make_request("/search", {"query": "deploy"})
    
    # Test 4: Search for something that doesn't exist
    make_request("/search", {"query": "nonexistent"})
    
    # Test 5: Empty query
    make_request("/search", {"query": ""})

def test_fetch_endpoint():
    """Test the fetch endpoint with various IDs"""
    print("\n📄 TESTING FETCH ENDPOINT")
    
    # Test 1: Fetch existing todos
    for todo_id in ["1", "2", "3", "4", "5"]:
        make_request("/fetch", {"id": todo_id})
    
    # Test 2: Fetch non-existent todo
    make_request("/fetch", {"id": "999"})
    
    # Test 3: Invalid ID format
    make_request("/fetch", {"id": "invalid"})

def test_error_cases():
    """Test error cases for both endpoints"""
    print("\n⚠️  TESTING ERROR CASES")
    
    # Search without query
    make_request("/search", {})
    
    # Fetch without id
    make_request("/fetch", {})
    
    # Test with non-JSON content
    print("\n" + "="*60)
    print("Testing non-JSON request")
    print("-" * 60)
    try:
        response = requests.post(f"{BASE_URL}/search", data="not json")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Acme Todo MCP Server Tests")
    print(f"Testing server at: {BASE_URL}")
    
    test_search_endpoint()
    test_fetch_endpoint()
    test_error_cases()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("Make sure to start the server with: python app.py")

if __name__ == "__main__":
    main()
