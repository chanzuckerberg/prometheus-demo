import logging
import sys
import os

import prometheus_client
from flask import Flask, Response, request
from prometheus_client import Histogram
from prometheus_client import start_http_server

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# globals
APP_NAME = 'prometheus-aggregator'
PORT = int(os.environ['PORT'])
TELE_PORT = int(os.environ['TELE_PORT'])
app = Flask(APP_NAME)

JOB_LATENCY = Histogram(
    'job_latency_seconds',
    'Cromwell job latencies in seconds',
    ['pipeline_id', 'stage_id', 'worker_id', 'status'],
    buckets=tuple([5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 60.0, 90.0, 120.0, 150.0, 180.0, 360.0, float("INF")])
)


# endpoint that exposes metrics to prometheus server
@app.route('/metrics')
def metrics():
    return Response(prometheus_client.generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')


# health check endpoint
@app.route('/health')
def health():
    return "OK"


@app.route('/job-metrics/<pipeline_id>', methods=['POST'])
def post_metrics(pipeline_id):
    stage_id = request.form.get('stage_id')
    worker_id = request.form.get('worker_id')
    seconds_str = request.form.get('seconds')
    status = request.form.get('status')
    try:
        seconds = float(seconds_str)
    except ValueError as e:
        return Response('Time parameter must be a valid float', 406)
    JOB_LATENCY.labels(pipeline_id, stage_id, worker_id, status).observe(seconds)
    return Response('Created', 201)


if __name__ == '__main__':
    start_http_server(TELE_PORT, '')
    app.run(host='0.0.0.0', port=PORT)
