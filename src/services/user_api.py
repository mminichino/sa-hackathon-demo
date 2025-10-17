import redis
import random
import json
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
from redis.commands.search.field import TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.exceptions import ResponseError

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

HOSTNAME = os.environ.get("REDIS_HOST", "localhost")
PORT = os.environ.get("REDIS_PORT", "6379")
PASSWORD = os.environ.get("REDIS_PASSWORD")

# Redis connection configuration
redis_client = redis.Redis(
    host=HOSTNAME,
    port=int(PORT),
    decode_responses=True,
    password=PASSWORD,
)

# Realistic user data with proper zipcodes
REALISTIC_USERS = [
    {
        "name": "John Doe",
        "location_address": "123 Main St, New York, NY",
        "zipcode": "10001",
        "city_state": "New York, NY"
    },
    {
        "name": "Sarah Johnson",
        "location_address": "456 Market St, San Francisco, CA",
        "zipcode": "94103",
        "city_state": "San Francisco, CA"
    },
    {
        "name": "Michael Chen",
        "location_address": "789 Michigan Ave, Chicago, IL",
        "zipcode": "60607",
        "city_state": "Chicago, IL"
    },
    {
        "name": "Emily Rodriguez",
        "location_address": "321 Ocean Dr, Miami, FL",
        "zipcode": "33139",
        "city_state": "Miami, FL"
    },
    {
        "name": "David Wilson",
        "location_address": "654 Pine St, Seattle, WA",
        "zipcode": "98101",
        "city_state": "Seattle, WA"
    },
    {
        "name": "Jessica Brown",
        "location_address": "987 Sunset Blvd, Los Angeles, CA",
        "zipcode": "90210",
        "city_state": "Los Angeles, CA"
    },
    {
        "name": "Robert Taylor",
        "location_address": "147 Congress St, Boston, MA",
        "zipcode": "02101",
        "city_state": "Boston, MA"
    },
    {
        "name": "Amanda Davis",
        "location_address": "258 Peachtree St, Atlanta, GA",
        "zipcode": "30309",
        "city_state": "Atlanta, GA"
    }
]

def generate_user_id():
    """Generate sequential user ID"""
    # Get existing user count to generate next ID
    user_count = 0
    for i in range(1, 1000):  # Check up to user999
        test_key = f"user:user{i:03d}:*"
        if not any(redis_client.scan_iter(match=test_key)):
            user_count = i
            break
    else:
        user_count = random.randint(100, 999)

    return f"user{user_count:03d}"

def get_random_user_data():
    """Get random realistic user data"""
    return random.choice(REALISTIC_USERS)

# Transaction generation data
MERCHANTS = [
    "Amazon Store", "Walmart", "Target", "Best Buy", "Home Depot",
    "Starbucks", "McDonald's", "Subway", "Pizza Hut", "KFC",
    "Gas Station Shell", "Chevron", "BP", "Exxon", "Mobil",
    "Fashion Boutique", "Electronics World", "Grocery Plus", "Book Store",
    "Coffee Shop", "Restaurant Deluxe", "Fast Food Corner", "Luxury Watches Ltd"
]

CARD_NUMBERS = [
    "4111 1111 1111 1111", "4222 2222 2222 2222", "4333 3333 3333 3333",
    "4444 4444 4444 4444", "4555 5555 5555 5555", "4666 6666 6666 6666"
]

def get_random_existing_user():
    """Get a random existing user from Redis"""
    pattern = "user:*"
    user_keys = list(redis_client.scan_iter(match=pattern))
    return random.choice(user_keys)

def generate_random_transaction():
    """Generate a random transaction for an existing user"""
    # Get random existing user
    user_key = get_random_existing_user()

    # Extract user_id and zipcode from key
    parts = user_key.split(':')
    user_id = parts[1]  # user001, user002, etc.
    zipcode = parts[2]  # 10001, 94103, etc.

    # Get user data from Redis
    user_data = redis_client.hgetall(user_key)
    if not user_data:
        raise Exception(f"User not found: {user_key}")

    # Generate transaction ID
    txn_id = f"txn_{random.randint(1000, 9999)}"

    # Generate transaction data
    transaction_data = {
        "transaction_id": txn_id,
        "user_id": user_id,
        "zipcode": zipcode,
        "location": user_data.get('location_address', 'Unknown'),
        "amount": round(random.uniform(10.0, 5000.0), 2),
        "currency": "USD",
        "card_number": random.choice(CARD_NUMBERS),
        "merchant_id": f"store_{random.randint(100, 999)}",
        "merchant_name": random.choice(MERCHANTS),
        "transaction_type": random.choice(["store", "online"]),
        "status": "pending",
        "device_id": f"dev_{random.choice(['a', 'b', 'c'])}{random.randint(100, 999)}",
        "timestamp": datetime.now().isoformat() + "Z",
        "is_fraud": False  # Always false as requested
    }

    return txn_id, transaction_data, user_id

def generate_fraudulent_transaction():
    """Generate a fraudulent transaction with suspicious patterns"""
    # Get random existing user
    user_key = get_random_existing_user()

    # Extract user_id and zipcode from key
    parts = user_key.split(':')
    user_id = parts[1]  # user001, user002, etc.
    zipcode = parts[2]  # 10001, 94103, etc.

    # Get user data from Redis
    user_data = redis_client.hgetall(user_key)
    if not user_data:
        raise Exception(f"User not found: {user_key}")

    # Generate transaction ID
    txn_id = f"txn_{random.randint(1000, 9999)}"

    # Define fraudulent patterns
    fraud_patterns = [
        {
            "type": "high_value_food",
            "merchant_name": "Uber Eats",
            "amount": round(random.uniform(800.0, 1500.0), 2),
            "description": "Unusually high food delivery amount"
        },
        {
            "type": "multiple_small_purchases",
            "merchant_name": "TikTok Shop",
            "amount": round(random.uniform(9.99, 19.99), 2),
            "description": "Small amount but part of rapid-fire purchases"
        },
        {
            "type": "luxury_electronics",
            "merchant_name": "Electronics World",
            "amount": round(random.uniform(2000.0, 8000.0), 2),
            "description": "High-value electronics purchase"
        },
        {
            "type": "foreign_location",
            "merchant_name": "International Store",
            "amount": round(random.uniform(500.0, 3000.0), 2),
            "description": "Purchase from unusual location"
        },
        {
            "type": "late_night_gas",
            "merchant_name": "24/7 Gas Station",
            "amount": round(random.uniform(200.0, 500.0), 2),
            "description": "Unusual late-night high-value gas purchase"
        },
        {
            "type": "luxury_shopping",
            "merchant_name": "Luxury Watches Ltd",
            "amount": round(random.uniform(5000.0, 15000.0), 2),
            "description": "High-value luxury item purchase"
        }
    ]

    # Select random fraud pattern
    fraud_pattern = random.choice(fraud_patterns)

    # Generate suspicious location (different from user's location)
    suspicious_locations = [
        "Unknown Location, International",
        "ATM Machine, Foreign Country",
        "Online Purchase, Suspicious IP",
        "Gas Station, Highway Rest Stop",
        "Mall Kiosk, Temporary Location"
    ]

    # Generate transaction data with fraud indicators
    transaction_data = {
        "transaction_id": txn_id,
        "user_id": user_id,
        "zipcode": zipcode,
        "location": random.choice(suspicious_locations),
        "amount": fraud_pattern["amount"],
        "currency": "USD",
        "card_number": random.choice(CARD_NUMBERS),
        "merchant_id": f"fraud_{random.randint(100, 999)}",
        "merchant_name": fraud_pattern["merchant_name"],
        "transaction_type": random.choice(["online", "card_present"]),
        "status": "",  # Fraudulent transactions often complete quickly
        "device_id": f"suspicious_dev_{random.randint(100, 999)}",
        "timestamp": datetime.now().isoformat() + "Z",
        "fraud_indicators": [],
        "is_fraud": "",  # Blank - AI will detect and update
        "risk_score": 0,  # Zero - AI will detect and update,
        "reasoning": "" 
    }

    return txn_id, transaction_data, user_id

@app.route('/')
def index():
    """Serve the main UI"""
    return send_from_directory('.', 'index.html')

@app.route('/logo.png')
def logo():
    """Serve the RediShield logo"""
    return send_from_directory('.', 'logo.png')

@app.route('/api/user', methods=['POST'])
def create_user():
    """
    Create a new user with realistic data
    Key format: user:user_id:zipcode
    """
    try:
        # Generate realistic user data
        user_data_template = get_random_user_data()
        user_id = generate_user_id()

        # Create Redis key: user:user_id:zipcode
        redis_key = f"user:{user_id}:{user_data_template['zipcode']}"

        # Check if user already exists
        if redis_client.exists(redis_key):
            return jsonify({
                'error': f'User already exists with key: {redis_key}',
                'status': 'failed'
            }), 409

        # Default password hash (for "hello" - as in your example)
        default_password_hash = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"

        # Prepare user data for Redis Hash
        user_data = {
            'name': user_data_template['name'],
            'user_id': user_id,
            'location_address': user_data_template['location_address'],
            'zipcode': user_data_template['zipcode'],
            'account_type': 'creditcard',
            'password_hash': default_password_hash,
            'created_at': datetime.now().isoformat()
        }

        # Store user data in Redis Hash
        redis_client.hset(redis_key, mapping=user_data)

        # Return success response (without password hash for security)
        response_data = user_data.copy()
        response_data['password_hash'] = "***hidden***"

        return jsonify({
            'message': 'User created successfully',
            'status': 'success',
            'redis_key': redis_key,
            'user_data': response_data
        }), 201

    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'failed'
        }), 500

@app.route('/api/transaction', methods=['POST'])
def create_transaction():
    """
    Create a random transaction for an existing user
    Stores in: JSON, Stream, and Sorted Set
    """
    try:
        # Generate random transaction
        txn_id, transaction_data, user_id = generate_random_transaction()

        # Create Redis keys
        redis_key = f"txn:{user_id}:{txn_id}"
        sorted_set_key = f"amount:{user_id}:transactionset"

        # 1. Store as JSON document
        redis_client.execute_command('JSON.SET', redis_key, '$', json.dumps(transaction_data))

        # 2. Add to Redis Stream
        stream_data = {}
        for key, value in transaction_data.items():
            stream_data[key] = str(value)

        stream_id = redis_client.xadd('transactions_stream', stream_data)

        # 3. Add to Sorted Set (amount as score)
        redis_client.zadd(sorted_set_key, {txn_id: transaction_data['amount']})

        # 4. Create Redis Search Index for transactions
        try:
            redis_client.ft("transactions-index").create_index(
                [TagField("$.user_id", as_name="user_id")],
                definition=IndexDefinition(
                    prefix=["txn:"],
                    index_type=IndexType.JSON
                )
            )
        except ResponseError:
            pass

        return jsonify({
            'status': 'success',
            'message': 'Transaction created, added to stream and sorted set',
            'redis_key': redis_key,
            'stream_id': stream_id,
            'sorted_set_key': sorted_set_key,
            'transaction': transaction_data
        }), 201

    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'failed'
        }), 500

@app.route('/api/fraud-transaction', methods=['POST'])
def create_fraud_transaction():
    """
    Create a fraudulent transaction with suspicious patterns
    Examples: High Uber Eats orders, TikTok shopping sprees, luxury purchases
    """
    try:
        # Generate fraudulent transaction
        txn_id, transaction_data, user_id = generate_fraudulent_transaction()

        # Create Redis keys
        redis_key = f"txn:{user_id}:{txn_id}"
        sorted_set_key = f"amount:{user_id}:transactionset"

        # 1. Store as JSON document
        redis_client.execute_command('JSON.SET', redis_key, '$', json.dumps(transaction_data))

        # 2. Add to Redis Stream
        stream_data = {}
        for key, value in transaction_data.items():
            stream_data[key] = str(value)

        stream_id = redis_client.xadd('transactions_stream', stream_data)

        # 3. Add to Sorted Set (amount as score)
        redis_client.zadd(sorted_set_key, {txn_id: transaction_data['amount']})

        return jsonify({
            'status': 'success',
            'message': '🚨 SUSPICIOUS transaction created - AI will analyze for fraud!',
            'redis_key': redis_key,
            'stream_id': stream_id,
            'sorted_set_key': sorted_set_key,
            'transaction': transaction_data,
            'ai_processing_note': {
                'is_fraud': 'Blank - AI will detect and update',
                'fraud_reason': 'Blank - AI will detect and update',
                'risk_score': 'Zero - AI will detect and update',
                'suspicious_patterns': [
                    'Unusual amount for merchant type',
                    'Suspicious location pattern',
                    'Device/timing anomalies'
                ]
            }
        }), 201

    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'failed'
        }), 500

@app.route('/api/user/<user>', methods=['GET'])
def get_user(user):
    pattern = f"user:{user}:*"
    user_keys = list(redis_client.scan_iter(match=pattern))

    if len(user_keys) > 0:
        user = redis_client.hgetall(user_keys[0])
        return jsonify(user), 200

    return jsonify({
        'error': f'User not found: {user}',
        'status': 'failed'
    }), 404

@app.route('/api/users/zipcode/<zipcode>', methods=['GET'])
def get_user_by_zipcode(zipcode):
    pattern = f"user:*:{zipcode}"
    user_keys = list(redis_client.scan_iter(match=pattern))

    if len(user_keys) > 0:
        result = {'users': [], 'count': len(user_keys)}
        for user_key in user_keys:
            user = redis_client.hgetall(user_key)
            user_data = {'redis_key': user_key, 'user_data': user}
            result['users'].append(user_data)
        return jsonify(result), 200

    return jsonify({
        'error': f'Users not found in zipcode: {zipcode}',
        'status': 'failed'
    }), 404

@app.route('/api/users/stats', methods=['GET'])
def get_user_stats():
    pattern = "user:*"
    user_keys = list(redis_client.scan_iter(match=pattern))

    if len(user_keys) > 0:
        users = []
        for user_key in user_keys:
            user = redis_client.hgetall(user_key)
            users.append(user)

        result = {'stats': {}}
        result['stats']['total_users'] = len(users)
        result['stats']['creditcard_users'] = sum(1 for u in users if u.get('account_type') == 'creditcard')
        result['stats']['debitcard_users'] = sum(1 for u in users if u.get('account_type') == 'debitcard')
        return jsonify(result), 200

    return jsonify({
        'error': f'Users not found',
        'status': 'failed'
    }), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        redis_client.ping()
        status = "online"
    except ConnectionError as e:
        status = f"offline: {e}"
    except Exception as e:
        status = f"error: {e}"

    result = {'status': status, 'redis_connection': f"{HOSTNAME}:{PORT}"}
    return jsonify(result), 200

def main():
    print("🛡️ Starting RediShield - Fraud Detection Protection Layer...")
    print("🚀 Emphasizing Redis as your protection layer")
    print("👥 User API - Redis Key Format: user:user_id:zipcode")
    print("💳 Transaction API - Redis Key Format: txn:user_id:transaction_id")
    print("🔗 Endpoints:")
    print("   GET / - RediShield Web UI")
    print("   POST /api/user - Create user with realistic data")
    print("   POST /api/transaction - Create random transaction")
    print("   POST /api/fraud-transaction - Create FRAUDULENT transaction for testing")
    print("📊 Features:")
    print("   ✅ Generates users from 8 major US cities")
    print("   ✅ Creates transactions with JSON, Stream, and Sorted Set storage")
    print("   ✅ Real zipcodes and locations")
    print("   ✅ Normal transactions: fraud score false")
    print("   🚨 Fraud transactions: suspicious patterns (high amounts, unusual locations)")
    print("   ✅ Redis-styled protection layer UI")

    app.run(debug=True, host='0.0.0.0', port=8081)

if __name__ == '__main__':
    main()
