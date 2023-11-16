from sessions import sso_session
import syslog

from metrics_definition import ec2_metrics_def

### EC2 Metrics Gathering ###

def ec2_gather():

    try:
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

    except Exception as e:
       # Registra cualquier excepción que ocurra durante la obtención de métricas        
        syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas EC2: {str(e)}')    