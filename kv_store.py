import logging
import sys
import os
import time
import json

import prometheus_client
from flask import Flask, Response, request, make_response
from prometheus_client import Counter, Histogram
from prometheus_client import start_http_server

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# globals
APP_NAME = 'prometheus-demo'
PORT = int(os.environ['PORT'])
TELE_PORT = int(os.environ['TELE_PORT'])
MEAN_LAG = float(os.environ.get('MEAN_LAG', '0.0'))
STUFF = {}
app = Flask(APP_NAME)

# prometheus data structures
# shamelessly stolen from https://github.com/sbarratt/flask-prometheus/blob/353dd1b6b50da90bc84fd8704730de39571debd4/build/lib/flask_prometheus/__init__.py#L24
FLASK_REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Flask Request Latency',
    ['app', 'method', 'endpoint']
)

FLASK_REQUEST_COUNT = Counter(
    'request_count',
    'Flask Request Count',
    ['app', 'method', 'endpoint', 'http_status']
)

# prometheus instrumentation for HTTP metrics
def before_request():
    request.start_time = time.time()


def after_request(response):
    request_latency = time.time() - request.start_time
    FLASK_REQUEST_LATENCY.labels(APP_NAME, request.method, request.url_rule).observe(request_latency)
    FLASK_REQUEST_COUNT.labels(APP_NAME, request.method, request.url_rule, response.status_code).inc()
    logger.info("{} {} {}".format(response.status_code, request.method, request.path))
    return response


def monitor(app, port, addr=''):
    app.before_request(before_request)
    app.after_request(after_request)
    start_http_server(port, addr)


# endpoint that exposes metrics to prometheus server
@app.route('/metrics')
def metrics():
    return Response(prometheus_client.generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')


# health check endpoint
@app.route('/health')
def health():
    return "OK"


# cache endpoint
@app.route('/cache/<key>', methods=['GET', 'PUT', 'DELETE'])
def stuff(key):
    global STUFF
    if request.method == 'PUT':
        STUFF[key] = request.data
        body = json.dumps({'status': 'OK'})
        status = 201
    elif request.method == 'DELETE':
        body = ''
        status = 204
    elif request.method == 'GET' and key not in STUFF:
        body = ''
        status = 204
    elif request.method == 'GET':
        body = STUFF[key]
        status = 200
    else:
        body = json.dumps({'status': 'Method Not Supported'})
        status = 406

    time.sleep(MEAN_LAG)

    return make_response(body, status)


if __name__ == '__main__':
    HOST = '0.0.0.0'
    monitor(app, port=TELE_PORT)
    app.run(host=HOST, port=PORT)

