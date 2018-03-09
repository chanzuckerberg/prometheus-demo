# Prometheus Demo

This repo simulates monitoring HTTP microservices and short-lived batched jobs with [Prometheus](prometheus.io).

Grafana is deployed alongside Prometheus with sample dashboards for visualizing the data.

## Setup

Before running any of the demonstrations below, you need to build the docker image for running the test kv_store and aggregator applications.

```bash
make image
```

To start the servers, use [docker-compose](https://docs.docker.com/compose/).

```bash
docker-compose up
```

You will have to wait a few minutes before metrics start to appear on the dashboards described in the following sections.

## Monitoring HTTP microservices

The `docker-compose.yaml` configuration sets up three instances of an HTTP key/value store microservice (similar to memcached).

* The code that implements of the key/value store with prometheus instrumentation in `kv_store.py`.
* The code that synthesizes traffic on these instances can be found in `simulate_http_traffic.py.`
* The Grafana server is preconfigured with a [dashboard for HTTP metrics](http://localhost:3000/d/Xq2D8b3kz/http-metrics?refresh=10s&orgId=1).

## Monitoring short-lived jobs

The `docker-compose.yaml` configuration sets up a metrics aggregator that short-lived jobs can send their metrics to.

* The code that implements the metrics aggregator lives in `aggregator.py`.
* The code that synthesizes batch job metrics is in `simulate_jobs.py`
* The Grafana server is preconfigured with a [dashboard job metrics](http://localhost:3000/d/RcrJyiRiz/job-statistics?refresh=30s&orgId=1).

## Operating the servers

You will then have the following servers running.

* [kv_store_server_0](http://localhost:8080/health)
* [kv_store_server_1](http://localhost:8081/health)
* [kv_store_server_2](http://localhost:8082/health)
* [prometheus](http://localhost:9090)
* [grafana](http://localhost:3000)
* [aggregator](http://localhost:5000/health)

You can check the metrics collection status of the kv_store servers on the [Prometheus targets page](http://localhost:9090/targets).

On the grafana server there is a sample [HTTP dashboard](http://localhost:3000/d/Xq2D8b3kz/http-metrics?orgId=1) showing off some standard http metrics.

## Teardown

Shut it down when you're done!

```bash
docker-compse down
```
