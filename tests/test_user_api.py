import requests
import json
import pytest

# API base URL
BASE_URL = "http://localhost:8081/api"

def test_create_user():
    """Test creating users"""
    print("🧪 Testing User Creation...")
    
    created_users = []
    
    for n in range(16):
        try:
            response = requests.post(f"{BASE_URL}/user")
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Created user: {result['redis_key']}")
                created_users.append(result['redis_key'])
            else:
                print(f"❌ Failed to create user: {response.json()}")
                
        except Exception as e:
            print(f"❌ Error creating user: {e}")
    
    return created_users

@pytest.mark.parametrize("user_key", ["user001"])
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

@pytest.mark.parametrize("zipcode", ["10001", "90210"])
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
