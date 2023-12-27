from sessions import sso_session
from datetime import datetime, timezone
from metrics_definition import health_metrics_def

import syslog
import json
### AWS HEALTH Metrics Gathering ###

def health_gather():

    try:
        # Obtiene información sobre todas las instancias
        health_response = sso_session.health_client.describe_events()

        # Obtiene la fecha y hora actuales
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)

        # Itera a través de las reservas y las instancias
        for event in health_response['events']:
            # Obtenemos el ARN del evento
            event_arn = event['arn']

            try:

                # Obtenemos los detalles del evento usando el ARN
                event_details_response = sso_session.health_client.describe_event_details(eventArns=[event_arn])
                # Obtnemos los recursos afectados
                affected_entities_response = sso_session.health_client.describe_affected_entities(filter={
                    'eventArns': [event_arn]
                })
                # Extraemos la información del evento desde la respuesta
                event_details = event_details_response['successfulSet'][0]['event']
                event_description =  event_details_response['successfulSet'][0]['eventDescription']

                service = event['service']
                region = event.get('region', 'N/A')
                eventType = event['eventTypeCode']
                statusCode = event.get('statusCode', 'N/A')
                startTime = event.get('startTime')
                lastUpdatedTime = event.get('lastUpdatedTime')
                latestDescription  = event_description['latestDescription'] # Accede a latestDescription en eventDescription
                arn = event_details['arn']
                eventTypeCategory = event_details['eventTypeCategory']
                eventScopeCode = event_details['eventScopeCode']

                # Extraemos las entidades afectadas y las convertimos en una lista de cadenas
                affected_entities = [entity['entityValue'] for entity in affected_entities_response.get('entities', [])]

                # Convierte startTime y lastUpdatedTime a objetos datetime con información de zona horaria si no lo son
                if startTime and not startTime.tzinfo:
                    startTime = startTime.replace(tzinfo=timezone.utc)
                if lastUpdatedTime and not lastUpdatedTime.tzinfo:
                    lastUpdatedTime = lastUpdatedTime.replace(tzinfo=timezone.utc)

                # Define y establece el valor de la métrica con las etiquetas
    #            if statusCode.lower() in ['open', 'upcoming'] and ((startTime and startTime > current_time) or (lastUpdatedTime and lastUpdatedTime > current_time)):
                if statusCode and  statusCode.lower() not in ['closed']:
                    for entity in affected_entities:
                        health_metrics_def.health_events_metric.labels(
                            service,
                            region,
                            eventType,
                            statusCode,
                            startTime,
                            lastUpdatedTime,
                            latestDescription,
                            arn,
                            eventTypeCategory,
                            eventScopeCode,
                            entity
                        ).set(1)

            except Exception as e:
                # Manejar la excepción al obtener detalles del evento
                syslog.syslog(syslog.LOG_ERR, f'Error al obtener detalles del evento {event_arn}: {str(e)}')

    except Exception as e:
       # Registra cualquier excepción que ocurra durante la obtención de métricas
        syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas de AWS HEALTH {str(e)}')