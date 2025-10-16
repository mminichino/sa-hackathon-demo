import json
import redis
import os
from typing import List
from src.services.fraudomatic import get_score
from src.services.db import get_user_transactions


def test_with_database():
    hostname = os.environ.get("REDIS_HOST")
    port = os.environ.get("REDIS_PORT")
    password = os.environ.get("REDIS_PASSWORD")

    if not hostname or not port or not password:
        raise Exception("Missing environment variables")

    print("Connecting to Redis")
    r = redis.Redis(
        host=hostname,
        port=int(port),
        password=password
    )

    docs = get_user_transactions(r, "user_001")
    transactions: List[dict] = []
    for doc in docs:
        data = doc.__dict__.get("json")
        doc_data = json.loads(str(data))
        transactions.append(doc_data)

    current = transactions[0]
    amounts = [txn['amount'] for txn in transactions]
    average_spend = sum(amounts) / len(amounts) if amounts else 0
    result = get_score(
        amount=str(current.get("amount")),
        merchant=str(current.get("merchant_name")),
        location=str(current.get("location")),
        time=str(current.get("location")),
        spend_average=str(average_spend),
        locations=[txn['location'] for txn in transactions],
        merchants=[txn['merchant_name'] for txn in transactions],
        recent_activity=transactions
    )

    print(json.dumps(result, indent=2))
