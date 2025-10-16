#!/usr/bin/env python3
"""
Simple Transaction API - Creates random transactions in Redis JSON format
"""

import redis
import json
import random
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Redis connection
redis_client = redis.Redis(
    host='redis-18507.c48014.us-central1-mz.gcp.cloud.rlrcp.com',
    port=18507,
    decode_responses=True,
    username="default",
    password="k9q8fDpI5kKXjeRmokTJTLJ8KImHMfHX",
)

def get_random_user():
    """Get random user from existing users in Redis"""
    user_keys = [
        "user001:10001",
        "user002:94103",
        "user003:60607",
        "user004:33139",
        "user005:98101"
    ]
    return random.choice(user_keys)

def generate_random_transaction():
    """Generate random transaction data using existing user data"""
    txn_id = f"txn_{random.randint(1000, 9999)}"

    # Get random user
    user_key = get_random_user()
    user_id, zipcode = user_key.split(':')

    # Try to get user data from Redis
    try:
        user_data = redis_client.hgetall(user_key)
        if user_data and 'location_address' in user_data:
            location = user_data['location_address']
        else:
            # Fallback locations based on zipcode
            zipcode_locations = {
                "10001": "New York, NY",
                "94103": "San Francisco, CA",
                "60607": "Chicago, IL",
                "33139": "Miami, FL",
                "98101": "Seattle, WA"
            }
            location = zipcode_locations.get(zipcode, "Unknown Location")
    except:
        location = "Unknown Location"

    card_numbers = [
        "4532 9843 2211 7745",
        "5555 4444 3333 2222",
        "4111 1111 1111 1111",
        "3782 822463 10005"
    ]
    merchants = [
        {"id": "store_110", "name": "Luxury Watches Ltd."},
        {"id": "store_220", "name": "Electronics World"},
        {"id": "store_330", "name": "Fashion Boutique"},
        {"id": "online_440", "name": "Amazon Store"}
    ]
    transaction_types = ["store", "online"]

    merchant = random.choice(merchants)

    transaction = {
        "transaction_id": txn_id,
        "card_number": random.choice(card_numbers),
        "user_id": user_id,
        "zipcode": zipcode,
        "merchant_id": merchant["id"],
        "merchant_name": merchant["name"],
        "amount": round(random.uniform(10.00, 5000.00), 2),
        "currency": "USD",
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "location": location,
        "device_id": f"dev_{random.choice(['a999', 'b888', 'c777', 'd666'])}",
        "transaction_type": random.choice(transaction_types),
        "status": random.choice(["approved", "pending", "declined"]),
        "is_fraud": False  # Always false as requested
    }

    return txn_id, transaction, user_id

@app.route('/api/transaction', methods=['POST'])
def create_transaction():
    """Create a random transaction"""
    try:
        # Generate random transaction
        txn_id, transaction_data, user_id = generate_random_transaction()

        # Redis key format: txn:user_id:transaction_id
        redis_key = f"txn:{user_id}:{txn_id}"

        # Store in Redis using JSON.SET
        redis_client.execute_command('JSON.SET', redis_key, '$', json.dumps(transaction_data))

        # Add to Redis Stream
        stream_data = {}
        for key, value in transaction_data.items():
            stream_data[key] = str(value)  # Convert all values to strings for stream

        stream_id = redis_client.xadd('transactions_stream', stream_data)

        # Add to Sorted Set (amount as score, transaction_id as member)
        sorted_set_key = f"amount:{user_id}:transactionset"
        redis_client.zadd(sorted_set_key, {txn_id: transaction_data['amount']})

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
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Transaction API...")
    print("📊 Creates random transactions for existing users")
    print("👥 Users: user001, user002, user003, user004, user005")
    print("� Adds to Redis Stream: transactions_stream")
    print("� Adds to Sorted Set: {user_id}:transactionset")
    print("��🔗 Endpoint: POST /api/transaction")
    app.run(debug=True, host='0.0.0.0', port=5001)
