from sessions import sso_session
import syslog

from metrics_definition import health_metrics_def

### HEALTH Metrics Gathering ###

def health_gather():

    try:
        # Obtiene información sobre los eventos de AWS Health
        health_response = sso_session.health_client.describe_events()

        # Itera a través de los eventos
        for event in health_response['events']:
            service = event['service']
            region = event.get('region', 'N/A')
            eventType = event['eventTypeCode']
            statusCode = event.get('statusCode', 'N/A')
            startTime = event.get('startTime')

            # Define y establece el valor de la métrica con las etiquetas
            health_metrics_def.health_events_metric.labels(
                service,
                region,
                eventType,
                statusCode,
                startTime
            ).set(1)if statusCode.lower() in ['open', 'upcoming'] else None

    except Exception as e:
       # Registra cualquier excepción que ocurra durante la obtención de métricas
        syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas de AWS HEALTH {str(e)}')
