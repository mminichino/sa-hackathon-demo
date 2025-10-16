import threading
import os
import redis
import time
import logging
from flask import Flask, jsonify
from .db import get_results, save_result

logging.basicConfig(level=logging.INFO, format='%(message)s')

HOSTNAME = os.environ.get("REDIS_HOST")
PORT = os.environ.get("REDIS_PORT")
PASSWORD = os.environ.get("REDIS_PASSWORD")

app = Flask(__name__)


def analyzer_loop(r):
    stream_name = 'transactions_stream'
    last_id = '0'

    while True:
        logging.info(f"Waiting for new messages in '{stream_name}'...")
        response = r.xread(streams={stream_name: last_id}, count=1, block=5000)

        if response:
            logging.info(f"New messages found")
            for stream, messages in response:
                logging.info(f"Stream: {stream}")
                for message_id, data in messages:
                    decoded_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
                    logging.info(f"Decoded data: {decoded_data}")
                    results = get_results(r, decoded_data)
                    logging.info(f"Results: {results}")
                    save_result(r, decoded_data, results)
                    r.xdel(stream_name, message_id)
                    logging.info(f"Deleted message {message_id} from stream")
                    last_id = message_id


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
