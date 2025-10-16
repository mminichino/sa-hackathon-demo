import os
import json

import pandas as pd
import streamlit as st
import redis

REDIS_URL = 'redis-18507.c48014.us-central1-mz.gcp.cloud.rlrcp.com:18507'
KEY_PATTERN = 'user:*'
PAGE_TITLE =  "RediSheild Demo"


@st.cache_resource(show_spinner=False)
def get_redis() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)

@st.cache_data(ttl=10, show_spinner=False)
def get_keys(pattern: str):
    r = get_redis()
    return sorted(list(r.scan_iter(match=pattern, count=100)))

st.set_page_config(page_title=PAGE_TITLE, layout="centered")
st.title(PAGE_TITLE)

users = get_keys('user:*')

if not users:
    st.warning(f"No users found.")
else:
    selected_user = st.selectbox(
        "User",
        users,
        index=None,
        placeholder="Select user...",
    )