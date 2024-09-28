import asyncio
import time
from scipy.stats import gamma
import math
import random


ATTRITION = 0

async def db_query(base, scale=0.02, sigma=1):
    global ATTRITION
    ATTRITION=+1
    duration = gamma.rvs(sigma, loc=base, scale=scale)
    await asyncio.sleep(duration + ATTRITION*gamma.rvs(5)/200)


def sync_process(base, scale=0.01, sigma=1):
    start = time.monotonic()
    duration = gamma.rvs(sigma, loc=base, scale=scale)
    while time.monotonic() - start < duration:
        math.sqrt(random.random()*23123123)

