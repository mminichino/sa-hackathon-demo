import os
import json

import pandas as pd
import streamlit as st
import redis

REDIS_URL = 'redis://default:k9q8fDpI5kKXjeRmokTJTLJ8KImHMfHX@redis-18507.c48014.us-central1-mz.gcp.cloud.rlrcp.com:18507'
REDIS_PASSWORD = 'k9q8fDpI5kKXjeRmokTJTLJ8KImHMfHX'
KEY_PATTERN = 'user:*'
PAGE_TITLE = "🛡️ RediShield Demo"

# Redis.io inspired styling
REDIS_STYLE = """
<style>
    /* Import Google Fonts for better typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Redis.io inspired colors and styling */
    :root {
        --redis-red: #DC382D;
        --redis-dark-red: #B8312A;
        --redis-orange: #FF6B35;
        --redis-dark-blue: #1A1A2E;
        --redis-light-gray: #F5F5F5;
        --redis-dark-gray: #2C2C54;
        --redis-white: #FFFFFF;
        --redis-green: #28A745;
        --redis-blue: #007BFF;
        --redis-fraud-red: #FF4444;
    }

    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, var(--redis-dark-blue) 0%, var(--redis-dark-gray) 100%);
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }

    .redis-logo {
        font-size: 2.5rem;
        color: var(--redis-red);
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }

    .logo-img {
        width: 60px;
        height: 60px;
        object-fit: contain;
    }

    .main-title {
        font-size: 3rem;
        color: var(--redis-red);
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-weight: 700;
    }

    .main-subtitle {
        font-size: 1.2rem;
        color: var(--redis-light-gray);
        margin-bottom: 1rem;
        opacity: 0.9;
    }

    /* Streamlit component overrides */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }

    .stSelectbox > div > div > div {
        color: var(--redis-white);
        background: transparent;
    }

    .stSelectbox label {
        color: var(--redis-orange) !important;
        font-weight: 600;
        font-size: 1.1rem;
    }

    /* DataFrame styling */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        width: 100% !important;
    }

    /* Make dataframe full width */
    .stDataFrame > div {
        width: 100% !important;
    }

    .stDataFrame iframe {
        width: 100% !important;
    }

    /* Force full width for all dataframe elements */
    .stDataFrame, .stDataFrame > div, .stDataFrame iframe,
    [data-testid="stDataFrame"], [data-testid="stDataFrame"] > div {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Container full width */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Force white text on all metric elements */
    .stMetric, .stMetric *,
    [data-testid="metric-container"],
    [data-testid="metric-container"] *,
    .st-emotion-cache-1q82h82,
    .e1wr3kle3,
    .st-emotion-cache-1q82h82.e1wr3kle3 {
        color: var(--redis-white) !important;
    }

    /* Override any black text in metrics */
    .stMetric [style*="color: black"],
    .stMetric [style*="color: rgb(0, 0, 0)"],
    [data-testid="metric-container"] [style*="color: black"],
    [data-testid="metric-container"] [style*="color: rgb(0, 0, 0)"] {
        color: var(--redis-white) !important;
    }

    /* Fix all markdown text to be white */
    .stMarkdown, .stMarkdown *,
    .stMarkdown p, .stMarkdown li,
    .stMarkdown strong, .stMarkdown em {
        color: var(--redis-white) !important;
    }

    /* Override any black text in markdown */
    .stMarkdown [style*="color: black"],
    .stMarkdown [style*="color: rgb(0, 0, 0)"] {
        color: var(--redis-white) !important;
    }

    /* Fix info box text color */
    .stAlert, .stAlert *,
    .stAlert p, .stAlert div {
        color: var(--redis-white) !important;
    }

    /* Override any dark text in alerts */
    .stAlert [style*="color: black"],
    .stAlert [style*="color: rgb(0, 0, 0)"],
    .stAlert [style*="color: rgb(49, 51, 63)"] {
        color: var(--redis-white) !important;
    }

    /* Text styling */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--redis-red);
        font-weight: 600;
    }

    .stMarkdown p {
        color: var(--redis-light-gray);
    }

    /* Metrics styling */
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .stMetric > div {
        color: var(--redis-white) !important;
    }

    .stMetric label {
        color: var(--redis-orange) !important;
        font-weight: 600;
        font-size: 1rem;
    }

    .stMetric [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid var(--redis-red);
    }

    .stMetric [data-testid="metric-container"] > div {
        color: var(--redis-white) !important;
    }

    .stMetric [data-testid="metric-container"] > div > div {
        color: var(--redis-white) !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }

    /* Fix specific Streamlit metric classes */
    .st-emotion-cache-1q82h82, .e1wr3kle3 {
        color: var(--redis-white) !important;
        background: transparent !important;
    }

    /* Target all metric value elements */
    [data-testid="metric-container"] .st-emotion-cache-1q82h82 {
        color: var(--redis-white) !important;
        font-weight: bold !important;
    }

    /* Metric labels */
    [data-testid="metric-container"] .st-emotion-cache-1q82h82.e1wr3kle3 {
        color: var(--redis-orange) !important;
        font-weight: 600 !important;
    }

    /* All metric text elements */
    .stMetric * {
        color: var(--redis-white) !important;
    }

    /* Specific targeting for metric values */
    .stMetric [data-testid="metric-container"] * {
        color: var(--redis-white) !important;
    }

    /* Warning and info boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        backdrop-filter: blur(10px);
        border-left: 4px solid var(--redis-orange);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(26, 26, 46, 0.9);
    }

    /* Custom fraud indicator */
    .fraud-indicator {
        background: var(--redis-fraud-red);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8rem;
    }

    .safe-indicator {
        background: var(--redis-green);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8rem;
    }
</style>
"""


@st.cache_resource(show_spinner=False)
def get_redis() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)

@st.cache_data(ttl=10, show_spinner=False)
def get_users(pattern: str):
    r = get_redis()
    return sorted(list(r.scan_iter(match=pattern, count=100)))

@st.cache_data(ttl=10, show_spinner=False)
def get_user_details(user_key: str):
    """Get user details from Redis hash"""
    r = get_redis()
    try:
        # Get all fields from the user hash
        user_data = r.hgetall(user_key)
        if user_data:
            return user_data
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching user details: {e}")
        return None

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

# Streamlit page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
st.markdown(REDIS_STYLE, unsafe_allow_html=True)

# Custom header with logo
st.markdown("""
<div class="main-header">
    <div class="redis-logo">
        <img src="http://localhost:5000/logo.png" alt="RediShield Logo" class="logo-img">
        🛡️ RediShield
    </div>
    <h1 class="main-title">Fraud Detection Protection Layer</h1>
    <p class="main-subtitle">Emphasizing Redis as your protection layer - View users and analyze transactions</p>
</div>
""", unsafe_allow_html=True)

users = get_users('user:*')

#clean up drop-down
user_ids = []
for u in users:
    user_id = u.split(":")[1]
    zip = u.split(":")[2]
    user_ids.append("User ID: " + user_id + ", ZIP Code: " + zip)

# Create two-column layout: left for controls, right for transactions
left_col, right_col = st.columns([1, 2])

with left_col:
    if not users:
        st.warning("🔍 No users found in Redis. Create some users first using the RediShield transaction generator!")
    else:
        st.markdown("### 👥 Select User to Analyze")
        selected_user = st.selectbox(
            "Choose a user to view their transactions:",
            users,
            index=None,
            placeholder="🔽 Select user...",
            help="Users are stored in Redis with the pattern: user:user_id:zipcode"
        )

        # Display user details if a user is selected
        if selected_user:
            st.markdown("---")
            st.markdown("### 👤 User Details")

            # Get user details from Redis
            user_details = get_user_details(selected_user)

            if user_details:
                # Parse user key to get user_id and zipcode
                user_parts = selected_user.split(":")
                user_id = user_parts[1] if len(user_parts) > 1 else "Unknown"
                zipcode = user_parts[2] if len(user_parts) > 2 else "Unknown"

                # Filter out sensitive data like password hash
                filtered_details = {k: v for k, v in user_details.items()
                                  if k.lower() not in ['password_hash', 'password', 'hash']}

                # Simple details display with line breaks
                details_lines = [f"User ID: {user_id}", f"ZIP Code: {zipcode}"]
                for key, value in filtered_details.items():
                    formatted_key = key.replace('_', ' ').title()
                    details_lines.append(f"{formatted_key}: {value}")

                details_text = "  \n".join(details_lines)
                st.markdown(details_text)
            else:
                st.warning(f"⚠️ No user details found for key: `{selected_user}`")
                st.info("This might be an empty hash or the key doesn't exist in Redis.")

with right_col:
    if 'selected_user' in locals() and selected_user:
        st.markdown("### 💳 Transaction Analysis")
        user_id = selected_user.split(":")[1]

        with st.spinner("🔍 Searching for transactions..."):
            transactions = get_transactions(user_id)

        if not transactions:
            st.info(f"💳 No transactions found for user **{user_id}**")
            st.markdown("*Create some transactions using the RediShield transaction generator on port 5000*")
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
                "risk_score",
                'fraud_indicators',
                'reasoning'
            ]
            cols_in_df = [c for c in preferred if c in df.columns]
            df = df[cols_in_df] if cols_in_df else df  # fallback to whatever is there

            # Type coercions for nicer sorting/formatting
            for num_col in ("amount",):
                if num_col in df.columns:
                    df[num_col] = pd.to_numeric(df[num_col], errors="coerce")
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

            # Count fraud transactions
            fraud_count = 0
            if "is_fraud" in df.columns:
                fraud_count = df["is_fraud"].sum() if df["is_fraud"].dtype == bool else (df["is_fraud"] == True).sum()

            # Display header with stats
            st.markdown("### 📊 User Analytics Dashboard")

            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("👤 User ID", user_id)
            with metric_col2:
                st.metric("💳 Total Transactions", len(df))
            with metric_col3:
                if fraud_count > 0:
                    st.metric("🚨 Fraud Alerts", fraud_count, delta=f"+{fraud_count}", delta_color="inverse")
                else:
                    st.metric("✅ Security Status", "All Clear", delta="No Fraud", delta_color="normal")

            st.markdown(f"### 📋 Transaction History for **{user_id}**")

            # Style the dataframe with fraud highlighting
            def highlight_fraud(row):
                if 'is_fraud' in row.index:
                    if row['is_fraud'] == True or row['is_fraud'] == 'true':
                        return ['background-color: rgba(255, 68, 68, 0.4); color: white; font-weight: bold'] * len(row)
                return [''] * len(row)

            # Apply styling and display with full screen width
            styled_df = df.style.apply(highlight_fraud, axis=1)

            # Use container to ensure full width
            with st.container():
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    height=500,
                    hide_index=True
                )

            # Add fraud legend
            if "is_fraud" in df.columns:
                st.markdown("""
                **Legend:**
                - 🟢 **Normal Transaction** - Standard transaction
                - 🔴 **Fraud Alert** - Highlighted in red background
                """)

            # Additional insights
            if fraud_count > 0:
                st.warning(f"⚠️ **Security Alert**: {fraud_count} potentially fraudulent transaction(s) detected for user {user_id}")
            else:
                st.success(f"✅ **All Clear**: No fraudulent activity detected for user {user_id}")
    else:
        st.markdown("### 📋 Transaction History")
        st.info("👈 Select a user from the dropdown to view their transaction history")
