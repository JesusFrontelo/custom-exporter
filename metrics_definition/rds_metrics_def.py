from prometheus_client import Gauge

# Define una metrica personalizada de Prometheus para AllocatedStorage
allocated_storage_metric = Gauge(
    'rds_allocated_storage',
    'Allocated Storage of RDS Instance',
    ['dbinstance_identifier', 'instance_class', 'engine_version', 'availability_zone', 'pending_maintenance', 'arn']
)

dbinstance_state_metric = Gauge(
    'rds_status',
    'Status of RDS Instance',
    ['dbinstance_identifier', 'instance_class', 'engine_version', 'availability_zone', 'pending_maintenance', 'status', 'arn']
)

dbinstance_maintenance_metric = Gauge (
    'rds_maintenance',
    'Maintenance Actions for RDS',
    ['dbinstance_identifier', 'instance_class', 'engine_version', 'availability_zone', 'pending_maintenance', 'arn', 'pending_action', 'pending_apply', 'pending_description']
)