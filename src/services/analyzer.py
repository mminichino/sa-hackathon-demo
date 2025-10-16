import threading
import os
import redis
import time
from flask import Flask, jsonify

HOSTNAME = os.environ.get("REDIS_HOST")
PORT = os.environ.get("REDIS_PORT")
PASSWORD = os.environ.get("REDIS_PASSWORD")

app = Flask(__name__)


def analyzer_loop(r):
    stream_name = 'transactions_stream'
    last_id = '$'

    while True:
        print(f"Waiting for new messages in '{stream_name}'...")
        response = r.xread(streams={stream_name: last_id}, count=1, block=0)

        if response:
            for stream, messages in response:
                for message_id, data in messages:
                    print(f"New message received!")
                    print(f"  ID: {message_id}")
                    print(f"  Data: {data}")
                    last_id = message_id

        time.sleep(5)


@app.route("/")
def read_root():
    return jsonify({"service": "analyzer"})


@app.route("/analyze")
def analyze():
    return jsonify({"status": "analyzing data"})


def main():
    print("Analyzer service is starting up")

    if not HOSTNAME or not PORT or not PASSWORD:
        raise Exception("Missing environment variables")

    print("Connecting to Redis")
    r = redis.Redis(
        host=HOSTNAME,
        port=int(PORT),
        password=PASSWORD
    )

    analyzer_thread = threading.Thread(target=analyzer_loop, args=(r,), daemon=True)
    analyzer_thread.start()
    app.run()

if __name__ == '__main__':
    main()
