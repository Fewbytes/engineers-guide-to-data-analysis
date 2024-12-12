# Graphing cheatsheet

    Every graph is an answer to a specific question. If you don't know what question this graph answers then the graph will mislead you.
    - Nukemberg

## Visual
We want to visually encode as much context as possible on graphs. This prevents misinterpretation of the graphs. 
 
- Avoid spaghetti graphs: Max 5 (related) lines per graph, see [metric clusters](#metric-clusters) below
- Avoid second Y axis, use multiple horizontal graphs instead
- Use high contrast color theme. Avoid mixing blue/green or other known color blindness combinations
- Always use units where applicable
- Use custom labels for series names
- Use [thresholds](https://grafana.com/docs/grafana/latest/panels-visualizations/configure-thresholds/) to communicate when metric crossed into problematic range
- Y Axis bounds: Bounds communicate what the "normal" or possible range of the metric is.
    - Consider how occasional spikes would look; automatic bounds means a spike will cause the rest of the graph to be "flat"
    - Max - Should probably be limited to "normal" range
    - Min - For zero bound metrics, this should probably be zero
- Give the graph a meaningful title and description; What question does this graph answer?

## Signal processing
- Use [moving averages](https://docs.victoriametrics.com/metricsql/#avg_over_time) or [Holt-Winters](https://docs.victoriametrics.com/metricsql/#holt_winters) to remove high frequency noise; See [Exponential smoothing](https://en.wikipedia.org/wiki/Exponential_smoothing) for more info.
    - Note: Smoothing will remove sporadic peaks. Combine with min/max over time to see series range (see [peak erosion](#peak-erosion) for more info) or consider creating separate graph for low frequency trends and high frequency peaks
- Use [linear regression](https://docs.victoriametrics.com/metricsql/#predict_linear) for monotonically increasing long term trends. E.g. when will the disk be full? when will memory be exhausted?
    - For more seasonal trends consider using Holt-Winters

## Metric clusters
When dealing with a group of similar metrics across some dimension - e.g. a used memory of service pods - avoid putting them all on a "spaghetti graph". Graphs with multiple lines are confusing and do not help understanding the behavior of the group. Instead, use derived series:
- Spread: Plot _min_, _max_ and _mean_ / _median_ of the group
- Most deviant: Use the _topk_ family of functions to select K series out of the group  