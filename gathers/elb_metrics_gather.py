from sessions import sso_session
import syslog
#import json

from metrics_definition import elb_metrics_def
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
    
            processed_bytes_statistics = sso_session.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/ApplicationELB',
                MetricName='ProcessedBytes',
                Dimensions=[
                    {'Name': 'LoadBalancer', 'Value': lb_arn_metric},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=60, # Intervalo de muestreo de 1 minuto
                Statistics=['Sum']
            )
            #print(json.dumps(processed_bytes_statistics, indent=4, default=str))    
            if 'Datapoints' in processed_bytes_statistics and processed_bytes_statistics['Datapoints']:
                elb_metrics_def.processed_bytes_metric.labels(
                    lb_name,
                    lb_arn
                ).set(processed_bytes_statistics['Datapoints'][0].get('Sum', 0))
    
            # Obtiene los grupos de destinos asociados a este balanceador de carga
            tg_response = sso_session.elb_client.describe_target_groups()
    
            # Itera sobre cada grupo de destinos
            for target_group in tg_response.get('TargetGroups', []):
                target_group_name = target_group.get('TargetGroupName')
                target_group_arn = target_group.get('TargetGroupArn')
    
                # Extrae la porción necesaria del ARN del grupo de destinos
                target_group_dimension = target_group_arn.split(':')[-1]
    
                # Consulta la métrica UnHealthyHostCount para el grupo de destinos
                unhealthy_host_count_metric = sso_session.cloudwatch_client.get_metric_statistics(
                    Namespace='AWS/ApplicationELB',
                    MetricName='UnHealthyHostCount',
                    Dimensions=[
                        {'Name': 'LoadBalancer', 'Value': lb_arn_metric},
                        {'Name': 'TargetGroup', 'Value': target_group_dimension},
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=60,  # Intervalo de muestreo de 1 minuto
                    Statistics=['Sum']
                )

                if 'Datapoints' in unhealthy_host_count_metric and unhealthy_host_count_metric['Datapoints']:
                    elb_metrics_def.unhealthy_host_metric.labels(
                        lb_name,
                        lb_arn,
                        target_group_name,
                        target_group_arn
                    ).set(unhealthy_host_count_metric['Datapoints'][0].get('Sum', 0))                
    
    except Exception as e:
       # Registra cualquier excepción que ocurra durante la obtención de métricas        
        syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas ELB: {str(e)}')