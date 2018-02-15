#!/usr/bin/env python3
import random
import binascii
import os
import time
import http.client
import urllib.parse


def random_select(lst):
    random_index = random.randrange(0, len(lst))
    return list(lst)[random_index]


def random_hexidecimal(n):
    return binascii.b2a_hex(os.urandom(n)).decode('utf-8')


def generate_pipeline_latencies(pipeline_id, worker_id):
    base_time = {
        '10x': 10.0,
        'smart-seq2': 6.0,
        'make-coffee': 45.0,
    }
    worker_latencies = {
        'worker1': 1.0,
        'worker2': 1.0,
        'worker3': 1.25,
    }
    latencies = {
        0: random.uniform(0.0, base_time[pipeline_id] * worker_latencies[worker_id]),
        1: random.uniform(0.0, (base_time[pipeline_id] * 2.0) * worker_latencies[worker_id]),
    }
    latencies['total'] = sum([latencies[0], latencies[1]])
    return latencies


def main():
    pipeline_ids = ['10x', 'smart-seq2', 'make-coffee']
    worker_ids = ['worker1', 'worker2', 'worker3']

    def gen_input_id():
        return random_hexidecimal(8)

    huge_input_id = gen_input_id()
    other_inputs = [gen_input_id() for i in range(9)]

    while True:
        pipeline_id = random_select(pipeline_ids)
        worker_id = random_select(worker_ids)

        latencies = generate_pipeline_latencies(pipeline_id, worker_id)

        for stage_id in [0, 1, 'total']:
            request_good = random.uniform(0.0, 1.0) < 0.98
            huge_input = random.uniform(0.0, 1.0) < 0.9
            latency = latencies[stage_id]

            if request_good:
                status = 'success'
            else:
                status = 'failure'

            if huge_input:
                input_id = huge_input_id
                latency += 10.0
            else:
                input_id = random_select(other_inputs)

            args = {
                'input_id': input_id,
                'worker_id': worker_id,
                'stage_id': stage_id,
                'status': status,
                'seconds': latency
            }
            conn = http.client.HTTPConnection('aggregator', 80)
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            conn.request('POST', '/job-metrics/' + pipeline_id, body=urllib.parse.urlencode(args), headers=headers)
            conn.getresponse()

        time.sleep(random.uniform(1.0, 10.0))


if __name__ == '__main__':
    main()
