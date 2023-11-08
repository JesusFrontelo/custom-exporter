####################################################################################
#####                                                                          #####
#####                               Metrics Gather                             #####
#####                                                                          #####
####################################################################################

import argparse
import sso_session
import ec2_metrics_def
import rds_metrics_def
from prometheus_client import start_http_server, Info

### Comenzamos la colecta de métricas ###

# Inicia el servidor Prometheus en el puerto especificado
start_http_server(sso_session.port)

while True:
    try:

        ### EC2 Metrics Gathering ###

        # Obtiene información sobre todas las instancias
        ec2_response = sso_session.ec2_client.describe_instances()

        # Itera a través de las reservas y las instancias
        for reservation in ec2_response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                state = instance['State']['Name']
                instance_type = instance['InstanceType']  # Obtiene el tipo de instancia
                launch_time = instance['LaunchTime']  # Obtiene el tipo de instancia

                # Convierte el tiempo de inicio en un valor numérico (timestamp) para Prometheus
                launch_timestamp = launch_time.timestamp()

                # Define y establece el valor de la métrica con la etiqueta de tipo de instancia
                ec2_metrics_def.instance_state_metric.labels(
                    instance_id,
                    instance_type,
                    state
                ).set(1 if state == 'running' else 0)

                # Define y establece el valor de la métrica con la etiqueta de tipo de instancia
                ec2_metrics_def.instance_launch_time_metric.labels(
                    instance_id,
                    instance_type,
                    state
                ).set(launch_timestamp)

        ### RDS Metrics Gathering ###

        # Obtiene una lista de todas las instancias RDS en la cuenta
        rds_response = sso_session.rds_client.describe_db_instances()

        if 'DBInstances' in rds_response:
            for db_instance in rds_response['DBInstances']:
                dbinstance_identifier = db_instance.get('DBInstanceIdentifier')
                allocated_storage = db_instance.get('AllocatedStorage')
                instance_class = db_instance.get('DBInstanceClass')
                engine_version = db_instance.get('EngineVersion')
                availability_zone = db_instance.get('AvailabilityZone')
                pending_maintenance = db_instance.get('PendingMaintenance')
                status = db_instance.get('DBInstanceStatus')

                if dbinstance_identifier and allocated_storage is not None:
                    rds_metrics_def.allocated_storage_metric.labels(
                        dbinstance_identifier,
                        instance_class,  # Agrega la etiqueta de clase de instancia
                        engine_version, # Agrega la etiqueta de version del engine
                        availability_zone, # Agrega la etiqueta de region la AZ
                        pending_maintenance, # Agrega la etiqueta del estado del pending maintenance
                        status # Agrega la etiqueta del estado de la RDS (available, stopped, creating ...)
                    ).set(allocated_storage)

    except Exception as e:
       print(f'Error al obtener métricas::{str(e).encode("utf-8")}')

    # Agrega un retardo (por ejemplo, 60 segundos) antes de volver a obtener los datos
    import time
    time.sleep(60)

i = Info('custom_exporter_build', 'Description of info')
i.info({'version': '0.1', 'Author': 'Jesús Frontelo'})