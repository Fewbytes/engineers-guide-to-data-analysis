from functools import partial
import os
import random
from typing import Awaitable, Callable
from fastapi import FastAPI, HTTPException, Request, Response
from opentelemetry import trace, metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.view import View, ExplicitBucketHistogramAggregation
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_INSTANCE_ID, OsResourceDetector, ProcessResourceDetector
from httpx import ASGITransport, AsyncClient
import psutil
from statsd.client import StatsClient
from sim import sync_process, db_query
import time
import asyncio


resource = Resource(attributes={SERVICE_NAME: "metrics-gen", SERVICE_INSTANCE_ID: "001"}).merge(OsResourceDetector().detect()).merge(ProcessResourceDetector().detect())
metrics_reader = PeriodicExportingMetricReader(OTLPMetricExporter(insecure=True), export_interval_millis=10000)
console_reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=10000)
meter_provider = MeterProvider(resource=resource,
                               views=[View(instrument_name="http.*",
                                           aggregation=ExplicitBucketHistogramAggregation(boundaries=[0.005*i for i in range(50)]))],
                               metric_readers=[metrics_reader, console_reader])
metrics.set_meter_provider(meter_provider)

app = FastAPI()
statsd = StatsClient()


http_meter = metrics.get_meter("http", "0.0.1")
# https://opentelemetry.io/docs/specs/semconv/http/http-metrics/
http_histogram = http_meter.create_histogram("http.server.duration")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    
    statsd.timing("statsd.http.server.duration.ok", process_time)
    http_histogram.record(process_time, {"http.method": request.method, "http.response.status_code": response.status_code,
                                         "http.route": request["path"]})
    return response



@app.get("/")
async def home():
    sync_process(0.05)
    await db_query(0.01)
    if random.random() < 0.1:
        raise HTTPException(status_code=500)

    sync_process(0.02)
    if random.random() < 0.1:
        await db_query(0.1, 0.05)
    sync_process(0.01)
    return {"status": "ok"}


@app.get("/slower")
async def slower():
    sync_process(0.02)
    await db_query(0.08, 0.05)
    if random.random() < 0.1:
        raise HTTPException(status_code=500)
    sync_process(0.01)
    

async def load_gen(path, sleep=0):
     async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        while True:
            await client.get(path)
            await asyncio.sleep(sleep)


def _cpu_time(options: metrics.CallbackOptions):
    return [metrics.Observation(time.process_time())]

cpu_meter = metrics.get_meter("cpu")
cpu_time_gauge = cpu_meter.create_observable_counter("process.cpu.time", [_cpu_time])


pid = os.getpid()
process = psutil.Process(pid)


def _memory_used(options: metrics.CallbackOptions):
    return [metrics.Observation(process.memory_info().rss)]
        
memory_meter = metrics.get_meter("memory")
memory_meter.create_observable_counter("process.memory.usage", [_memory_used])


event_loop_meter = metrics.get_meter("event_loop")
lag_histogram = event_loop_meter.create_histogram("python.event_loop.lag", unit="ms")


def _measure_event_loop_lag(last=None):
    if last:
        lag_histogram.record(time.perf_counter_ns()*1000 - last - 10)
    asyncio.get_event_loop().call_later(10, partial(_measure_event_loop_lag, time.perf_counter_ns()*1000))


async def main(concurrency=5):
    print("Starting pseudo load generation")
    await asyncio.gather(*([load_gen("/", 0.01) for _ in range(concurrency)] +
                           [load_gen("/slower", 0.1) for _ in range(2)]))



loop = asyncio.new_event_loop()
loop.call_soon(_measure_event_loop_lag)
loop.run_until_complete(main())