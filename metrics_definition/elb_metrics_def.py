from prometheus_client import Gauge

# Métricas con etiquetas
active_connections_metric = Gauge(
    'elb_active_connections',
    'Número de conexiones activas en el LB',
    ['lb_name', 'lb_arn']
)

new_connections_metric = Gauge(
    'elb_new_connections',
    'Número de nuevas conexiones en el LB',
    ['lb_name', 'lb_arn']
)

# Define la métrica de Prometheus para ProcessedBytes
processed_bytes_metric = Gauge(
    'elb_processed_bytes',
    'Número total de bytes procesados por ELB',
    ['lb_name', 'lb_arn']
)