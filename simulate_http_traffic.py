#!/usr/bin/env python3
import random
import http.client
import os
import time
import binascii
from random import randrange


HOSTS = ['kv_store_0', 'kv_store_1', 'kv_store_2']
PORT = 80


def random_select(lst):
    random_index = randrange(0, len(lst))
    return list(lst)[random_index]


def random_hexidecimal(n):
    return binascii.b2a_hex(os.urandom(n)).decode('utf-8')


def main():
    written_keys = set([])
    while True:
        request_good = random.uniform(0.0, 1.0) < 0.98
        host = random_select(HOSTS)

        if request_good:
            if len(written_keys) > 3000:
                method = 'DELETE'
                key = written_keys.pop()
                body = ''
            else:
                method = 'PUT' if len(written_keys) == 0 or random.uniform(0.0, 1.0) > 0.5 else 'GET'
                if method == 'PUT':
                    key = random_hexidecimal(10)
                    written_keys.add(key)
                else:
                    key = random_select(written_keys)
                body = random_hexidecimal(100)
        else:
            method = random_select(['HEAD', 'POST'])
            key = random_hexidecimal(10)
            body = ''

        conn = http.client.HTTPConnection(host, PORT)
        conn.request(method, '/cache/' + key, body)
        response = conn.getresponse()
        print(' '.join([str(response.status), method, '/cache/', key]))

        time.sleep(random.uniform(0.1, 1.0))


if __name__ == '__main__':
    main()
