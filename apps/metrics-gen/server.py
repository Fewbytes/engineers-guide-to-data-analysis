import random
from fastapi import FastAPI, HTTPException
from opentelemetry import trace, metrics
from httpx import ASGITransport, AsyncClient
from statsd.client import StatsClient
from sim import sync_process, db_query
import asyncio

app = FastAPI()
statsd = StatsClient()


# https://opentelemetry.io/docs/specs/semconv/http/http-metrics/

boot_meter = metrics.get_meter("app_boot")
boot_counter = boot_meter.create_counter("myapp.boot")


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


async def main(concurrency=5):
    print("Starting pseudo load generation")
    boot_counter.add(1)
    await asyncio.gather(*([load_gen("/", 0.01) for _ in range(concurrency)] +
                           [load_gen("/slower", 0.1) for _ in range(2)]))



loop = asyncio.new_event_loop()
loop.run_until_complete(main())