from prometheus_client.core import GaugeMetricFamily, REGISTRY
from sessions import sso_session
import syslog
import json
import re

class RDSMetricsCollector:
    def collect(self):
        try:
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
                    tags = self.get_rds_tags(db_instance)

                    # Métrica de almacenamiento asignado
                    if 'DBClusterIdentifier' not in db_instance:
                        if dbinstance_identifier and allocated_storage is not None:
                            rds_allocated_storage = GaugeMetricFamily(
                                'rds_allocated_storage',
                                'Allocated storage for RDS instances',
                                labels=['dbinstance_identifier', 'arn'] + list(tags.keys())
                            )
                            rds_allocated_storage.add_metric(
                                [dbinstance_identifier, arn] + list(tags.values()),
                                allocated_storage
                            )
                            yield rds_allocated_storage

                    # Métrica de estado de la instancia
                    if dbinstance_identifier and allocated_storage is not None:
                        rds_status = GaugeMetricFamily(
                            'rds_status',
                            'State of RDS instances',
                            labels=['dbinstance_identifier', 'state', 'arn'] + list(tags.keys())
                        )
                        rds_status.add_metric(
                            [dbinstance_identifier, status, arn] + list(tags.values()),
                            1 
                        )
                        yield rds_status

                    # Métricas de mantenimiento pendiente
                    pending = sso_session.rds_client.describe_pending_maintenance_actions(Filters=[{'Name': 'db-instance-id', 'Values': [arn]}])
                    actions = pending.get('PendingMaintenanceActions', [])

                    for action in actions:
                        for action_detail in action['PendingMaintenanceActionDetails']:
                            pending_action = action_detail.get('Action')
                            pending_apply = action_detail.get('CurrentApplyDate', 'N/A')
                            date2 = pending_apply.strftime("%Y-%m-%d") if pending_apply != 'N/A' else "N/A"
                            pending_description = action_detail.get('Description', 'N/A')
                            eventTypeCode = "RDS MAINTENANCE"

                            if 'oracle' in engine:
                                pattern = r"available on (\d{4}-\d{2}-\d{2})"
                                match = re.search(pattern, pending_description)
                                if match:
                                    date2 = match.group(1)
                                    pending_apply = date2

                            if pending_apply != 'N/A':
                                rds_maintenance = GaugeMetricFamily(
                                    'rds_maintenance',
                                    'Maintenance metrics for RDS instances',
                                    labels=['dbinstance_identifier', 'engine_version', 'preferred_maintenance_window', 'arn', 'pending_action', 'pending_apply', 'pending_description', 'eventTypeCode'] + list(tags.keys())
                                )
                                rds_maintenance.add_metric(
                                    [dbinstance_identifier, engine_version, preferred_maintenance_window, arn, pending_action, str(pending_apply), pending_description, eventTypeCode] + list(tags.values()),
                                    1
                                )
                                yield rds_maintenance

        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas RDS: {str(e)}')
            print(f'Error al obtener métricas RDS: {str(e)}')  # Imprime el error en la consola para depuración

    def get_rds_tags(self, db_instance):
        """Obtiene todas las etiquetas de una instancia RDS automáticamente."""
        tags = {}
        for tag in db_instance['TagList']:
            tags[tag['Key']] = tag['Value']
        return tags