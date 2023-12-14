from prometheus_client import Gauge

# Metricas para eventos de AWS Health
health_events_metric = Gauge(
    'aws_health_events',
    'Número de eventos de AWS Health',
    ['service', 'region', 'eventType', 'statusCode', 'startTime']
)
