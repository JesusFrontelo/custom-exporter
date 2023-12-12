from sessions import sso_session
import syslog

from metrics_definition import rds_metrics_def

def rds_gather():

    try:

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
                arn = db_instance.get('DBInstanceArn')                

                if dbinstance_identifier and allocated_storage is not None:
                    rds_metrics_def.allocated_storage_metric.labels(
                        dbinstance_identifier,
                        instance_class,  # Agrega la etiqueta de clase de instancia
                        engine_version, # Agrega la etiqueta de version del engine
                        availability_zone, # Agrega la etiqueta de region la AZ
                        pending_maintenance, # Agrega la etiqueta del estado del pending maintenance
                        arn # Agrega la etiqueta del ARN de la RDS
                    ).set(allocated_storage)

                if dbinstance_identifier and allocated_storage is not None:
                    rds_metrics_def.dbinstance_state_metric.labels(
                        dbinstance_identifier,
                        instance_class,  # Agrega la etiqueta de clase de instancia
                        engine_version, # Agrega la etiqueta de version del engine
                        availability_zone, # Agrega la etiqueta de region la AZ
                        pending_maintenance, # Agrega la etiqueta del estado del pending maintenance
                        status, # Agrega la etiqueta del estado de la RDS (available, stopped, creating ...)
                        arn # Agrega la etiqueta del ARN de la RDS
                    ).set(1 if status == 'available' else 0)

    except Exception as e:
       # Registra cualquier excepción que ocurra durante la obtención de métricas
        syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas RDS: {str(e)}')