import syslog

from sessions import sso_session
from gathers.functions import application_elb
from datetime import datetime, timedelta

### ELB Metrics Gathering ###
def elb_gather():

    try:

        elb_response = sso_session.elb_client.describe_load_balancers()

        for lb in elb_response.get('LoadBalancers', []):
            lb_name = lb.get('LoadBalancerName')
            lb_arn = lb.get('LoadBalancerArn')

            # Transformamos el arn para poder pasarlo en las dimensiones de la métrica
            lb_arn_split=lb_arn.split(':')
            lb_arn_metric = lb_arn_split[-1].replace('loadbalancer/', '')

            # Usa datetime para obtener las marcas de tiempo en formato ISO 8601
            start_time = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
            end_time = datetime.utcnow().isoformat()

            # Obtenemos las metricas mediante llamada a las funciones
            processed_bytes_statistics = application_elb.get_processed_bytes_metrics(
                sso_session.cloudwatch_client, lb_arn_metric, start_time, end_time, lb_name, lb_arn
            )

            # Obtiene los grupos de destinos asociados a este balanceador de carga
            tg_response = sso_session.elb_client.describe_target_groups()

            # Itera sobre cada grupo de destinos
            for target_group in tg_response.get('TargetGroups', []):
                target_group_name = target_group.get('TargetGroupName')
                target_group_arn = target_group.get('TargetGroupArn')

                # Extrae la porción necesaria del ARN del grupo de destinos
                target_group_dimension = target_group_arn.split(':')[-1]

                unhealthy_host_statistics = application_elb.get_unhealthy_host_metrics(
                    sso_session.cloudwatch_client, lb_arn_metric, target_group_dimension, start_time, end_time, lb_name, lb_arn, target_group_name, target_group_arn
                )

    except Exception as e:
       # Registra cualquier excepción que ocurra durante la obtención de métricas
        syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas ELB: {str(e)}')