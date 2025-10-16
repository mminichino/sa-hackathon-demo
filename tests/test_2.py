import json
import redis
import os
from unittest.mock import patch, MagicMock
from src.services.fraudomatic import get_score


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

    result = get_score(
        amount=50.0,
        merchant="Familiar Store",
        location="Familiar Location",
        time="2025-10-16T10:00:00Z",
        spend_average=55.0,
        locations=["Familiar Location"],
        merchants=["Familiar Store"],
        recent_activity=[]
    )

    print(json.dumps(result, indent=2))
