from prometheus_client.core import GaugeMetricFamily, REGISTRY
from sessions import sso_session
import syslog

class EC2MetricsCollector:
    def collect(self):
        try:
            # Obtiene información sobre todas las instancias
            ec2_response = sso_session.ec2_client.describe_instances()

            for reservation in ec2_response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    state = instance['State']['Name']
                    instance_type = instance['InstanceType']
                    launch_time = instance['LaunchTime']
                    tags = self.get_ec2_tags(instance)

                    # # Convierte el tiempo de inicio en un valor numérico (timestamp) para Prometheus
                    launch_timestamp = launch_time.timestamp()
                    
                    # Métrica de estado de la instancia
                    ec2_instance_state = GaugeMetricFamily(
                        'ec2_instance_state',
                        'State of EC2 instances',
                        labels=['instance_id', 'instance_type', 'state'] + list(tags.keys())
                    )
                    ec2_instance_state.add_metric(
                        [instance_id, instance_type, state] + list(tags.values()),
                        1 if state == 'running' else 0
                    )
                    yield ec2_instance_state

                    # Métrica de tiempo de lanzamiento de la instancia
                    ec2_instance_launch_time = GaugeMetricFamily(
                        'ec2_instance_launch_time',
                        'Launch time of EC2 instances',
                        labels=['instance_id', 'instance_type'] + list(tags.keys())
                    )
                    ec2_instance_launch_time.add_metric(
                        [instance_id, instance_type] + list(tags.values()),
                        launch_timestamp
                    )
                    yield ec2_instance_launch_time

        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas EC2: {str(e)}')
            print(f'Error al obtener métricas EC2: {str(e)}')  # Imprime el error en la consola para depuración

    def get_ec2_tags(self, instance):
        """Obtiene todas las etiquetas de una instancia EC2 automáticamente, excluyendo 'Platform'."""
        tags = {}
        if 'Tags' in instance:
            for tag in instance['Tags']:
#                if tag['Key'] not in ['Patch Group']:
                if tag['Key'] != 'Patch Group':  # Excluir la etiqueta 'Platform'
                    tags[tag['Key']] = tag['Value']
        return tags    
    
#    def get_ec2_tags(self, instance):
#        """Obtiene todas las etiquetas de una instancia EC2 automáticamente."""
#        tags = {}
#        if 'Tags' in instance:
#            for tag in instance['Tags']:
#                tags[tag['Key']] = tag['Value']
#        return tags