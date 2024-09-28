from opentelemetry.sdk.resources import Resource, OsResourceDetector, ProcessResourceDetector, SERVICE_NAME, SERVICE_INSTANCE_ID
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.view import View, ExplicitBucketHistogramAggregation
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry import metrics

resource = Resource(attributes={SERVICE_NAME: "metrics-gen", SERVICE_INSTANCE_ID: "001"}).merge(OsResourceDetector().detect()).merge(ProcessResourceDetector().detect())
metrics_reader = PeriodicExportingMetricReader(OTLPMetricExporter(insecure=True), export_interval_millis=10000)
console_reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=10000)
meter_provider = MeterProvider(resource=resource,
                               views=[View(instrument_name="http.*",
                                           aggregation=ExplicitBucketHistogramAggregation(boundaries=[0.005*i for i in range(50)]))],
                               metric_readers=[metrics_reader, console_reader])
metrics.set_meter_provider(meter_provider)
