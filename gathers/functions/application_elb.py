import syslog

from metrics_definition import elb_metrics_def

def get_processed_bytes_metrics(client, lb_arn_metric, start_time, end_time, lb_name, lb_arn):
    try:
        processed_bytes = client.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='ProcessedBytes',
            Dimensions=[
                {'Name': 'LoadBalancer', 'Value': lb_arn_metric},
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,  # Intervalo de muestreo de 1 minuto
            Statistics=['Sum']
        )

        if 'Datapoints' in processed_bytes and processed_bytes['Datapoints']:

            elb_metrics_def.processed_bytes_metric.labels(
                lb_name,
                lb_arn
            ).set(processed_bytes['Datapoints'][0].get('Sum', 0))

    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, f'Error en get_processed_bytes_metrics: {str(e)}')

def get_unhealthy_host_metrics(client, lb_arn_metric, target_group_dimension, start_time, end_time, lb_name, lb_arn, target_group_name, target_group_arn):
    try:
        unhealthy_host_count = client.get_metric_statistics(
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

        if 'Datapoints' in unhealthy_host_count and unhealthy_host_count['Datapoints']:
            elb_metrics_def.unhealthy_host_metric.labels(
                lb_name,
                lb_arn,
                target_group_name,
                target_group_arn
            ).set(unhealthy_host_count['Datapoints'][0].get('Sum', 0))

    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, f'Error en get_unhealthy_host_metrics: {str(e)}')