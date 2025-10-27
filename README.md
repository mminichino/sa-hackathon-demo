# Redis Fraud Detection Demo

A simple Flask API that generates random financial transactions and stores them in Redis using multiple data structures for fraud detection demos.

## 🎯 What This Code Does

The `transaction_api.py` file creates a single-endpoint Flask API that:

1. **Randomly selects** an existing user from Redis (user001-user005)
2. **Fetches user location** from their Redis Hash data
3. **Generates realistic transaction data** with random amounts, merchants, and card numbers
4. **Stores the transaction** in Redis using 3 different data structures simultaneously

## ⚙️ Setup
1. Clone this repo
2. Copy `example.env` to `.env` and update the OpenAI key and Redis connection details
3. Run `docker compose up -d`

```shell
cp example.env .env
```
```shell
docker compose up -d
```

The API helper UI can be accessed at http://127.0.0.1:8081.
The Demo UI can be accessed at http://127.0.0.1:8501.

Use the API helper UI to create users and transactions. Use the Demo UI to view the data.

## 🔧 How It Works

### Step 1: Random User Selection
```python
def get_random_user():
    user_keys = ["user001:10001", "user002:94103", "user003:60607", "user004:33139", "user005:98101"]
    return random.choice(user_keys)
```

### Step 2: Location Lookup
```python
user_data = redis_client.hgetall(user_key)
location = user_data['location_address']  # Gets actual user location
```

### Step 3: Transaction Generation
```python
transaction = {
    "transaction_id": "txn_1234",
    "user_id": "user002",
    "location": "San Francisco, CA",  # From user's Redis data
    "amount": 2887.06,               # Random $10-$5000
    "merchant_name": "Fashion Boutique",
    "transaction_type": "online",    # Random: store/online
    "is_fraud": false               # Always false
}
```

### Step 4: Triple Storage
```python
# 1. JSON Document
redis_client.execute_command('JSON.SET', 'txn:user002:txn_1234', '$', json.dumps(transaction))

# 2. Stream Entry
redis_client.xadd('transactions_stream', transaction_data)

# 3. Sorted Set (amount as score)
redis_client.zadd('amount:user002:transactionset', {'txn_1234': 2887.06})
```

## 📊 The API Endpoint

### POST `/api/transaction`
**What it does**: Creates one random transaction and stores it in Redis

**Usage**:
```bash
curl -X POST http://localhost:5001/api/transaction
```

**What happens when you call it**:
1. Picks a random user (user001, user002, user003, user004, or user005)
2. Gets their location from Redis Hash: `HGETALL user:user002:94103`
3. Generates random transaction data (amount, merchant, card, etc.)
4. Stores in 3 places:
   - **JSON**: `JSON.SET txn:user002:txn_1053 $ {...}`
   - **Stream**: `XADD transactions_stream * field1 value1 field2 value2...`
   - **Sorted Set**: `ZADD amount:user002:transactionset 2887.06 txn_1053`

**Response**:
```json
{
  "status": "success",
  "redis_key": "txn:user002:txn_1053",
  "stream_id": "1760637507602-0",
  "sorted_set_key": "amount:user002:transactionset",
  "transaction": {
    "transaction_id": "txn_1053",
    "user_id": "user002",
    "location": "San Francisco, CA",
    "amount": 2887.06,
    "is_fraud": false
  }
}
```

## 🗄️ Where Data Gets Stored

### 1. JSON Documents (Structured Data)
```bash
Key: txn:user002:txn_1053
Command: JSON.SET txn:user002:txn_1053 $ '{"transaction_id":"txn_1053",...}'
Purpose: Store complete transaction details for queries
```

### 2. Redis Streams (Real-time Processing)
```bash
Stream: transactions_stream
Command: XADD transactions_stream * transaction_id txn_1053 amount 2887.06 ...
Purpose: Real-time transaction feed for fraud detection
```

### 3. Sorted Sets (Analytics)
```bash
Key: amount:user002:transactionset
Command: ZADD amount:user002:transactionset 2887.06 txn_1053
Purpose: Sort transactions by amount for analysis
```

## 👥 Which Users It Uses

The code randomly picks from these 5 users that must already exist in Redis:

| User Key | Location |
|----------|----------|
| `user:user001:10001` | New York, NY |
| `user:user002:94103` | San Francisco, CA |
| `user:user003:60607` | Chicago, IL |
| `user:user004:33139` | Miami, FL |
| `user:user005:98101` | Seattle, WA |

## � How to Run

```bash
# Install dependencies
pip install flask redis

# Run the API
python3 transaction_api.py

# API starts on port 5001
# Call it: curl -X POST http://localhost:5001/api/transaction
```

## � Key Functions in the Code

### `get_random_user()`
```python
def get_random_user():
    user_keys = ["user001:10001", "user002:94103", ...]
    return random.choice(user_keys)
```
**Purpose**: Randomly picks one of the 5 existing users

### `generate_random_transaction()`
```python
def generate_random_transaction():
    # 1. Get random user
    user_key = get_random_user()

    # 2. Fetch their location from Redis
    user_data = redis_client.hgetall(user_key)
    location = user_data['location_address']

    # 3. Generate random transaction data
    transaction = {...}

    return txn_id, transaction, user_id
```
**Purpose**: Creates realistic transaction with user's actual location

### `create_transaction()` (API Endpoint)
```python
@app.route('/api/transaction', methods=['POST'])
def create_transaction():
    # Generate transaction
    txn_id, transaction_data, user_id = generate_random_transaction()

    # Store in 3 places
    redis_client.execute_command('JSON.SET', redis_key, '$', json.dumps(transaction_data))
    redis_client.xadd('transactions_stream', stream_data)
    redis_client.zadd(sorted_set_key, {txn_id: transaction_data['amount']})
```
**Purpose**: The main API endpoint that handles POST requests

## 📝 What Gets Generated

Each transaction includes:
- **Random amount**: $10.00 - $5,000.00
- **Random merchant**: "Luxury Watches Ltd", "Electronics World", etc.
- **Random card**: Test card numbers only
- **Random type**: "store" or "online"
- **User's real location**: From their Redis Hash data
- **Fraud flag**: Always `false`
- **Timestamp**: Current time in ISO format

## 🎯 Summary

**transaction_api.py** is a simple Flask app with one endpoint that:
1. Picks a random existing user
2. Gets their location from Redis
3. Generates fake transaction data
4. Stores it in Redis 3 different ways for fraud detection demos

**That's it!** Very simple but creates realistic data for testing fraud detection systems.
