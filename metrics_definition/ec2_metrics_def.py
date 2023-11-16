from prometheus_client import Gauge

# Define una métrica de Prometheus para el estado de las instancias
instance_state_metric = Gauge(
    'ec2_instance_state', 
    'Estado de las instancias EC2', 
    ['instance_id', 'instance_type', 'state']
    )


# Define una métrica de Prometheus para el launch time de las instancias
instance_launch_time_metric = Gauge(
    'ec2_launch_time',
    'Hora de inicio de las instancias EC2',
    ['instance_id', 'instance_type', 'state']
    )
