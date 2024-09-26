---
# You can also start simply with 'default'
theme: default
# some information about your slides (markdown enabled)
title: Engineer's guide to Data Analysis
info: |
  Engineer's guide to Data Analysis is a workshop designed to teach Observability from the ground up
# apply unocss classes to the current slide
class: text-center
# https://sli.dev/features/drawing
drawings:
  persist: false
# slide transition: https://sli.dev/guide/animations.html#slide-transitions
transition: slide-left
# enable MDC Syntax: https://sli.dev/features/mdc
mdc: true
---

# Engineer's guide to Data Analysis
## Avishai Ish-Shalom

---

# Today's show: A workshop in 4 acts

1. Fundamentals
1. Metrics design
1. Telemetry pipelines & storage
1. Data visualization and analysis

---
layout: section
---

# Act I: Fundamentals

---

# Telemetry
Collection of measurements from remote devices
- No direct observation is possible
- Build a a model of what's going on based on data

---
layout: statement
---
# How much data?

## 1k events/sec x 1k pods x 24 hours

Your computer generates _billions_ of events/sec

---
layout: statement
---
# Telemetry is *big data* problem

---

# Pillars of observability

|      |  |
|------|--|
| Logs | Big, verbose |
| Metrics | Lossy compression |
| Traces | Pre aggregated by transaction, compact, allow sampling|


---

# Where does data come from?

- Events: a reactive record of something that happened 
- Probes: a pro-active measurement of underlying state

Events can be _logged_ or aggregated as _metrics_ or _traces_


::div{class="footer"}
⚠️ bias ahoi! not all things are manifested as events
::

---

# Logs

Timestamped record of an event, preferably _structured_

- Often prioritized by _level_
- Tagged for filtering, usually by module
- Enriched with attributes, e.g. who wrote the log, context IDs 

```
{
  "@timestamp": "2024-10-29T11:54:01.407Z",
  "log.level": "INFO",
  "message": "Request handler started",
  "ecs.version": "1.2.0",
  "service.name": "some-service",
  "process.thread.name": "http-nio-8080-exec-8",
  "log.logger": "faboulus.app.http"
}
```

---

# Metrics

An arithmetic aggregation of events over time

- Count of some event type
- Some computation over events _value_ attribute
- Computed over a time interval

Metrics are _lossy_ compression


---
layout: image-right
image: https://opentelemetry.io/img/waterfall-trace.svg
backgroundSize: contain
---

# Traces

- Aggregate events by context ID
- Collection of _spans_
- _Spans_ aggregate start/end events of processing phases
- Context data
- Require context ID propagation
- Consistent sampling

---
layout: section
---

# Act II: Metrics design
## (Scary Math time!)

---

# Time series basics

`[(time, value)...]`
- _X_ axis is _time_
- One point per interval/bucket/window
- Characteristic _resolution_
- Bounded/unbounded value

![](/images/timeseries.svg)
---

# Basic types

- Counters
- Gauges
- Aggregates
- Histogram aggregates

---

# Aggregations
Time window can have many datapoints, derive a "representative" number

- Max/Min
- Average/mean
- Percentiles
- Reverse Quantiles
- Variance, StdDev

---

# Rollups: The peak erosion problem

- Downsampling: original time window has N points, new window has K points
- Need to aggregate N points into K points
- All aggregates will lose some data
- Most common is _averaging_

Prefer _counter_ over _gauge_

---

# Percentiles

99th percentile := value P which divides a group such that 99% of values <= P
- Actual member of the group
- `sorted(values)[int(len(values)*99/100)]`
- $O(n)$ memory, $O(n \log n)$ computation

---

# Exercise: Aggregating percentiles

- Is the sum of P99 values equal to P99 of sums?
- What about averages?
- What happens when a faulty process is aggregated with a normal process?

---

# Reverse quantiles
- What percentage of the group is above/bellow threshold?
- Computationally cheap: $O(1)$ memory, $O(n)$ computation
- Perfect for SLO
- Can be aggregated: $RQ(\sum metrics) = \sum RQ(metrics)$

---
layout: image-right
image: https://i.sstatic.net/393rs.png
backgroundSize: contain
---

# Historgrams
Basically, a group of _reverse quantiles_
- Aggregation friendly
- Take more space (depends on number of bins)
- Bins can selected smartly

---

# Metrics design 101
- Start with system model
- Inputs/outputs, boundaries
- Internal state
- List of questions

---
layout: image-right
image: ./images/how-to-measure-anything-book.jpg
---

# How to measure anything
- Measurements are approximation/bounds, not accurate
- Incremental, we can always get more data
- Measurements have cost, expected value, ROI

---

# Leading and Lagging metrics

- Leading metric - indication that something _will_ happen
  - System model artifact
  - Depend on model assumptions
- Lagging metric - indication that something _has_ happened
  - Concrete information - model input
  - Often too lagging to drive action

---

# Resolution
- ~ 5 datapoints to establish a trend
- _Time to detection_ > `Latency + 5*time_interval`
- Storage
- Rollups

💡 Multiple resolutions per single metric

---

# USE model
Resource oriented model

- Utilization
- Saturation: overflow, rejected
- Errors

Credit: [Brendan Gregg](https://www.brendangregg.com/usemethod.html)

---

# RED model
Processing phase / request oriented

- Rate
- Errors
- Duration (latency)

---
layout: image-right
image: /images/queueing-network.svg
backgroundSize: contain
---

# Jackson networks / Queueing analysis

- Throughput
- Processing latency
- Overall latency
- Rejections
- Processing errors
- Queue length

Invariants: Little's Law, throughput sum

---

# Let's monitor a parking lot

![](/images/parking-lot.svg)

---

# Metrics design checklist
- Model
- Questions
- Resolution
- Instrument boundaries, inputs, outputs
- Probes for internal state


---

# Exercise: App monitoring

- Resources: Memory, Connection pools, Event loop
- Events: GC
- Transactions

---
layout: section
---

# Act III: Telemetry pipelines & storage

---

![](./images/telemetry-pipeline.svg)


---
layout: image-right
image: https://opentelemetry.io/img/logos/opentelemetry-horizontal-color.svg
backgroundSize: contain
---

# What is OpenTelemetry?

- Cross platform standard API+SDK for metrics, traces & logs
- Instrumentation libraries
- Data collection protocols + collectors

---
layout: section
---

# StatsD
## An industry coming-of-age story

---

# StatsD
Originally a project from Etsy, [open sourced 2011](https://www.etsy.com/codeascraft/measure-anything-measure-everything/)

- Client, server and protocol
- Originally UDP based, lossy by design
- Designed for lossy aggregation and sampling
- Lightweight, simple


```
login.latency.ok:203.1|ms|@0.1
```
---

# Small project, high impact
- Scores of StatsD clones
- De facto standard protocol
- Brought metrics to the masses


---

# But, some inherent issues
- Original server in Node.js
- Percentiles, aggregated in server
- Correlated loss, metric skews
- Lots of underlying assumptions people missed

---

# Pipeline design

- Fault isolation from primary system
- (Over)load management: Loss vs Latency
- Aggregation partitioning: e.g. percentiles
- Retention, availability
- Emergency access

---
layout: image-right
image: /images/pipeline-aggregation-stages.svg
backgroundSize: contain
---

# Aggregate where?
Aggregation can (and does) happen in all stages
- Early aggregation --> less data, limited usage
- Late aggregation --> More data, more uses
- Partial aggregation
- Temporal aggregation

---

# Retention, resolution
Different needs, different data

- Emergencies
  - Usually 24h is long enough
  - But need high cardinality, high res
- Capacity planning, BI, etc
  - Long time frames (years)
  - Low resolution is ok

Often different Data engines too

---

# Message bus pipeline
![](/images/telemetry-pipeline-kafka.svg)

---

# Cluster?

![](/images/telemetry-pipeline-k8s.svg)


---

# Redudancy

![](/images/telemetry-pipeline-redundant.svg)

---
layout: section
---

# Act IV: Data visualization and analysis

---

# Visualization 101

- Every graph is an answer to a question
- Graphs often looked at during emergencies
  - Design for low cognitive overhead
  - Less is more
- Dashboards vs Interactive analysis
- Shared language

---

# Context matters
- Some metrics are related, need to be shown together
- Reference values: normal/abnormal
  - What is "big"? Is 102 a lot?

---

# Encoding context in visualization

---
layout: statement
class: big-quote
---

> Uptime is an illusion caused by lack of monitoring
>   <footer><cite>@nukemberg</cite></footer>