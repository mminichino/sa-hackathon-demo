#!/usr/bin/env python3
"""
Test script for User Management API
Demonstrates creating users and testing API endpoints
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000/api"

def test_create_user():
    """Test creating users"""
    print("🧪 Testing User Creation...")
    
    # Sample users for fraud detection testing
    test_users = [
        {
            "name": "John Doe",
            "user_id": "user001",
            "location_address": "123 Main St, New York, NY",
            "zipcode": "10001",
            "account_type": "creditcard",
            "password": "secure123"
        },
        {
            "name": "Jane Smith",
            "user_id": "user002", 
            "location_address": "456 Oak Ave, Los Angeles, CA",
            "zipcode": "90210",
            "account_type": "debitcard",
            "password": "mypassword456"
        },
        {
            "name": "Bob Johnson",
            "user_id": "user003",
            "location_address": "789 Pine St, New York, NY", 
            "zipcode": "10001",
            "account_type": "creditcard",
            "password": "bobsecure789"
        },
        {
            "name": "Alice Brown",
            "user_id": "user004",
            "location_address": "321 Elm St, Chicago, IL",
            "zipcode": "60601", 
            "account_type": "debitcard",
            "password": "alice2023"
        }
    ]
    
    created_users = []
    
    for user in test_users:
        try:
            response = requests.post(f"{BASE_URL}/user", json=user)
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Created user: {result['redis_key']}")
                created_users.append(result['redis_key'])
            else:
                print(f"❌ Failed to create user {user['user_id']}: {response.json()}")
                
        except Exception as e:
            print(f"❌ Error creating user {user['user_id']}: {e}")
    
    return created_users

def test_get_user(user_key):
    """Test getting a user by key"""
    print(f"\n🔍 Testing Get User: {user_key}")
    
    try:
        response = requests.get(f"{BASE_URL}/user/{user_key}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved user: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Failed to get user: {response.json()}")
            
    except Exception as e:
        print(f"❌ Error getting user: {e}")

def test_get_users_by_zipcode(zipcode):
    """Test getting users by zipcode"""
    print(f"\n📍 Testing Get Users by Zipcode: {zipcode}")
    
    try:
        response = requests.get(f"{BASE_URL}/users/zipcode/{zipcode}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['count']} users in zipcode {zipcode}")
            for user in result['users']:
                print(f"   - {user['redis_key']}: {user['user_data']['name']}")
        else:
            print(f"❌ Failed to get users by zipcode: {response.json()}")
            
    except Exception as e:
        print(f"❌ Error getting users by zipcode: {e}")

def test_get_stats():
    """Test getting user statistics"""
    print(f"\n📊 Testing User Statistics...")
    
    try:
        response = requests.get(f"{BASE_URL}/users/stats")
        
        if response.status_code == 200:
            result = response.json()
            stats = result['stats']
            print(f"✅ User Statistics:")
            print(f"   Total Users: {stats['total_users']}")
            print(f"   Credit Card Users: {stats['creditcard_users']}")
            print(f"   Debit Card Users: {stats['debitcard_users']}")
        else:
            print(f"❌ Failed to get stats: {response.json()}")
            
    except Exception as e:
        print(f"❌ Error getting stats: {e}")

def test_health_check():
    """Test health check endpoint"""
    print(f"\n🏥 Testing Health Check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Health: {result['status']}")
            print(f"   Redis Connection: {result['redis_connection']}")
        else:
            print(f"❌ Health check failed: {response.json()}")
            
    except Exception as e:
        print(f"❌ Error in health check: {e}")

def main():
    """Main test function"""
    print("=== User Management API Test Suite ===")
    print("🚀 Make sure the API server is running on localhost:5000")
    print()
    
    # Wait a moment for user to start the server
    input("Press Enter when the API server is running...")
    
    # Test health check first
    test_health_check()
    
    # Test creating users
    created_users = test_create_user()
    
    if created_users:
        # Test getting a specific user
        test_get_user(created_users[0])
        
        # Test getting users by zipcode
        test_get_users_by_zipcode("10001")
        test_get_users_by_zipcode("90210")
        
        # Test getting statistics
        test_get_stats()
    
    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    main()
