from sessions import sso_session
import syslog
import json
from metrics_definition import rds_metrics_def
import re

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
                engine = db_instance.get('Engine')
                availability_zone = db_instance.get('AvailabilityZone')
                preferred_maintenance_window = db_instance.get('PreferredMaintenanceWindow')
                status = db_instance.get('DBInstanceStatus')
                arn = db_instance.get('DBInstanceArn')
#                print (db_instance.get('Engine'))

                if dbinstance_identifier and allocated_storage is not None:
                    rds_metrics_def.allocated_storage_metric.labels(
                        dbinstance_identifier,
                        instance_class,  # Agrega la etiqueta de clase de instancia
                        engine_version, # Agrega la etiqueta de version del engine
                        arn # Agrega la etiqueta del ARN de la RDS
                    ).set(allocated_storage)

                if dbinstance_identifier and allocated_storage is not None:
                    rds_metrics_def.dbinstance_state_metric.labels(
                        dbinstance_identifier,
                        instance_class,  # Agrega la etiqueta de clase de instancia
                        engine_version, # Agrega la etiqueta de version del engine
                        availability_zone, # Agrega la etiqueta de region la AZ
                        preferred_maintenance_window, # Agrega la etiqueta del estado del pending maintenance
                        status, # Agrega la etiqueta del estado de la RDS (available, stopped, creating ...)
                        arn # Agrega la etiqueta del ARN de la RDS
                    ).set(1 if status == 'available' else 0)


                # Datos de la RDS.
                pending = sso_session.rds_client.describe_pending_maintenance_actions(Filters=[{'Name': 'db-instance-id', 'Values': [arn]}])
                actions = pending.get('PendingMaintenanceActions', [])
#                print(json.dumps(pending, indent=4, default=str))

                for action in actions:
                    for action_detail in action['PendingMaintenanceActionDetails']:
#                        print(json.dumps(action_detail, indent=4, default=str))
                        pending_action = action_detail.get('Action')
                        pending_apply = action_detail.get('CurrentApplyDate', 'N/A')
                        date2 = pending_apply.strftime("%Y-%m-%d") if pending_apply != 'N/A' else "N/A"
                        pending_description = action_detail.get('Description', 'N/A')

                        if 'oracle' in engine:
                            pattern = r"available on (\d{4}-\d{2}-\d{2})"
                            match = re.search(pattern, pending_description)
                            if match:
                                date2 = match.group(1)
                                pending_apply = date2

                                rds_metrics_def.dbinstance_maintenance_metric.labels(
                                    dbinstance_identifier,
                                    engine_version, # Agrega la etiqueta de version del engine
                                    preferred_maintenance_window, # Agrega la etiqueta del estado del pending maintenance
                                    arn, # Agrega la etiqueta del ARN de la RDS
                                    pending_action, # Agrega la etiqueta con la acción de mantenimiento que se va a realizar en la rds
                                    pending_apply, # Agrega la etiqueta con el estado de la aplicación de mantenimiento
                                    pending_description # Agrega la etiqueta con la descripción de las acciones a realizar
                                ).set(1)

                        if pending_apply is not 'N/A':
                            rds_metrics_def.dbinstance_maintenance_metric.labels(
                                dbinstance_identifier,
                                engine_version, # Agrega la etiqueta de version del engine
                                preferred_maintenance_window, # Agrega la etiqueta del estado del pending maintenance
                                arn, # Agrega la etiqueta del ARN de la RDS
                                pending_action, # Agrega la etiqueta con la acción de mantenimiento que se va a realizar en la rds
                                pending_apply, # Agrega la etiqueta con el estado de la aplicación de mantenimiento
                                pending_description # Agrega la etiqueta con la descripción de las acciones a realizar
                            ).set(1)


    except Exception as e:
       # Registra cualquier excepción que ocurra durante la obtención de métricas
        syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas RDS: {str(e)}')
