#!/usr/bin/env python3
"""
Simple User Creation API for Fraud Detection System
Creates users using Redis Hash datatype with key format: user_id:zipcode
"""

import redis
import hashlib
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Redis connection configuration
redis_client = redis.Redis(
    host='redis-18507.c48014.us-central1-mz.gcp.cloud.rlrcp.com',
    port=18507,
    decode_responses=True,
    username="default",
    password="k9q8fDpI5kKXjeRmokTJTLJ8KImHMfHX",
)

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_account_type(account_type):
    """Validate account type"""
    valid_types = ['creditcard', 'debitcard']
    return account_type.lower() in valid_types

@app.route('/api/user', methods=['POST'])
def create_user():
    """
    Create a new user with Redis Hash datatype
    Key format: user_id:zipcode
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'user_id', 'location_address', 'zipcode', 'account_type', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'status': 'failed'
                }), 400

        # Validate account type
        if not validate_account_type(data['account_type']):
            return jsonify({
                'error': 'Invalid account_type. Must be "creditcard" or "debitcard"',
                'status': 'failed'
            }), 400

        # Create Redis key: user_id:zipcode
        redis_key = f"{data['user_id']}:{data['zipcode']}"

        # Check if user already exists
        if redis_client.exists(redis_key):
            return jsonify({
                'error': f'User already exists with key: {redis_key}',
                'status': 'failed'
            }), 409

        # Hash the password
        hashed_password = hash_password(data['password'])

        # Prepare user data for Redis Hash
        user_data = {
            'name': data['name'],
            'user_id': data['user_id'],
            'location_address': data['location_address'],
            'zipcode': data['zipcode'],
            'account_type': data['account_type'].lower(),
            'password_hash': hashed_password,
            'created_at': datetime.now().isoformat()
        }

        # Store user data in Redis Hash
        redis_client.hset(redis_key, mapping=user_data)

        # Return success response (without password hash)
        response_data = user_data.copy()
        del response_data['password_hash']

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

if __name__ == '__main__':
    print("🚀 Starting Simple User Creation API...")
    print("📊 Redis Key Format: user_id:zipcode")
    print("🔗 Endpoint: POST /api/user - Create user")

    app.run(debug=True, host='0.0.0.0', port=5000)
