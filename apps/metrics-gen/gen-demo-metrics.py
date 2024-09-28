#!/usr/bin/env uv run
# requires-python = ">=3.12"
# dependencies = [
#   "orjson",
#   "requests",
#   "scipy",
#   "numpy",
#
#]

import requests
from scipy.stats import gamma
import numpy as np
import orjson as json
import time

def to_metric_json(name, labels, timestamps, values):
    return json.dumps({"metric": {"__name__": name, **labels},
                       "values": values,
                       "timestamps": timestamps
                       })



n=3600
resolution=1 # sec
signal = gamma.rvs(2.2, size=n)
now = time.time()
timestamps = np.linspace(now - n*resolution, now, n, dtype=np.int64)*1000


def send_metric(url):
    resp = requests.post("http://localhost:8428/api/v1/import", data=to_metric_json("test1", {"host": "demo"}, timestamps.tolist(), signal.tolist()))
    print(f"HTTP {resp.status_code}")