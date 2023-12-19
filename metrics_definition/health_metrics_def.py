from prometheus_client import Gauge

# Define una metrica personalizada de Prometheus para AllocatedStorage
health_events_metric = Gauge(
    'aws_health_events',
    'Número de eventos de AWS Health',
    ['service',
     'region',
     'eventTypeCode',
     'statusCode',
     'startTime',
     'lastUpdatedTime',
     'latestDescription',
      'arn',
      'eventTypeCategory',
      'availabilityZone',
      'eventScopeCode',
      'affected_entities'
    ]
)