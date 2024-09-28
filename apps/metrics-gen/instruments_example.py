from functools import partial
from opentelemetry import metrics
import time
import asyncio
import psutil
import os


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
