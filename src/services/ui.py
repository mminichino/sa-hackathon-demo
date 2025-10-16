import os
import json

import pandas as pd
import streamlit as st
import redis

REDIS_URL = 'redis://default:k9q8fDpI5kKXjeRmokTJTLJ8KImHMfHX@redis-18507.c48014.us-central1-mz.gcp.cloud.rlrcp.com:18507'
REDIS_PASSWORD = 'k9q8fDpI5kKXjeRmokTJTLJ8KImHMfHX'
KEY_PATTERN = 'user:*'
PAGE_TITLE =  "RediSheild Demo"


@st.cache_resource(show_spinner=False)
def get_redis() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)

@st.cache_data(ttl=10, show_spinner=False)
def get_users(pattern: str):
    r = get_redis()
    return sorted(list(r.scan_iter(match=pattern, count=100)))

def get_transactions(user):
    r = get_redis()
    query = "@user_id:{" + user + "}"
    result = r.execute_command("FT.SEARCH", "transactions-index", query)
    records = []
    for i in range(1, len(result), 2):
        key = result[i]
        fields = result[i + 1]  # This is already a list
        # Convert field-value pairs into a dict
        record = json.loads(fields[1])
        records.append(record)
    print(records)
    return records

#streamlit elements
st.set_page_config(page_title=PAGE_TITLE, layout="centered")
st.title(PAGE_TITLE)

users = get_users('user:*')

if not users:
    st.warning(f"No users found.")
else:
    selected_user = st.selectbox(
        "User",
        users,
        index=None,
        placeholder="Select user...",
    )
    if selected_user:
        user_id = selected_user.split(":")[1]
        transactions = get_transactions(user_id)
        # Convert to DataFrame
        if not transactions:
            st.info(f"No transactions found for {user_id}")
        else:
            # Make a DataFrame
            df = pd.DataFrame(transactions)

            # If your FT.SEARCH returned JSON-path-like keys (e.g. "$.transaction_id"),
            # strip them once when building records, or do it here:
            df = df.rename(columns=lambda c: c.lstrip("$."))

            # Drop the Redis key column (keep only JSON fields)
            if "_key" in df.columns:
                df = df.drop(columns=["_key"])

            # (Optional) Choose a preferred column order if present
            preferred = [
                "transaction_id",
                "card_number",
                "user_id",
                "merchant_id",
                "merchant_name",
                "amount",
                "currency",
                "timestamp",
                "location",
                "device_id",
                "transaction_type",
                "status",
                "is_fraud",
            ]
            cols_in_df = [c for c in preferred if c in df.columns]
            df = df[cols_in_df] if cols_in_df else df  # fallback to whatever is there

            # (Optional) type coercions for nicer sorting/formatting
            for num_col in ("amount",):
                if num_col in df.columns:
                    df[num_col] = pd.to_numeric(df[num_col], errors="coerce")
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

            st.subheader(f"Transactions for {user_id}")
            st.dataframe(df, use_container_width=True)
