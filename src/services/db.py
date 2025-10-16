import json
import logging
from json import JSONDecodeError

from redis import Redis
from redis.commands.search.query import Query
from redis.commands.search.document import Document
from typing import List, Optional
from .fraudomatic import get_score

def get_user_transactions(r: Redis, user_id: str) -> list[Document]:
    query_string = f"@user_id:{{{user_id}}}"
    result = r.ft("transactions-index").search(Query(query_string))
    return result.docs

def get_results(r: Redis, txn: dict):
    docs = get_user_transactions(r, str(txn.get("user_id")))
    logging.info(f"Found {len(docs)} transactions for user {txn.get('user_id')}")
    transactions: List[dict] = []
    for doc in docs:
        data = doc.__dict__.get("json")
        doc_data = json.loads(str(data))
        transactions.append(doc_data)

    amounts = [t['amount'] for t in transactions]
    average_spend = sum(amounts) / len(amounts) if amounts else 0
    result = get_score(
        amount=str(txn.get("amount")),
        merchant=str(txn.get("merchant_name")),
        location=str(txn.get("location")),
        time=str(txn.get("timestamp")),
        spend_average=str(average_spend),
        locations=[t['location'] for t in transactions],
        merchants=[t['merchant_name'] for t in transactions],
        recent_activity=transactions
    )

    try:
        return json.loads(result)
    except JSONDecodeError:
        logging.error(f"Error parsing JSON: {result}")
        return {}

def save_result(r: Redis, txn: dict, result: dict):
    user_id = str(txn.get("user_id"))
    txn_id = str(txn.get("transaction_id"))
    key = f"txn:{user_id}:{txn_id}"

    existing_data: dict = r.json().get(key)

    if existing_data:
        logging.info(f"Updating existing data for transaction {key}")
        if result.get("risk_score", 0) >= 0.5:
            existing_data["status"] = "declined"
            existing_data["is_fraud"] = True
        else:
            existing_data["status"] = "approved"
            existing_data["is_fraud"] = False
        existing_data["risk_score"] = result.get("risk_score", 0)
        existing_data["fraud_indicators"] = result.get("fraud_indicators", [])
        existing_data["reasoning"] = result.get("reasoning", "None")
        r.json().set(key, '$', existing_data)
    else:
        logging.warning(f"No existing data found for transaction {key}")
