from prometheus_client.core import GaugeMetricFamily, REGISTRY
from sessions import sso_session
from datetime import datetime, timezone
import syslog
import json

class HealthMetricsCollector:
    def collect(self):
        try:
            # Obtiene información sobre todos los eventos de salud
            health_response = sso_session.health_client.describe_events()

            for event in health_response['events']:
                event_arn = event['arn']

                try:
                    # Obtenemos los detalles del evento usando el ARN
                    event_details_response = sso_session.health_client.describe_event_details(eventArns=[event_arn])
                    affected_entities_response = sso_session.health_client.describe_affected_entities(filter={
                        'eventArns': [event_arn]
                    })

                    event_details = event_details_response['successfulSet'][0]['event']
                    event_description = event_details_response['successfulSet'][0]['eventDescription']

                    service = event['service']
                    region = event.get('region', 'N/A')
                    eventTypeCode = event['eventTypeCode']
                    statusCode = event.get('statusCode', 'N/A')
                    startTime = event.get('startTime')
                    lastUpdatedTime = event.get('lastUpdatedTime')
                    latestDescription = event_description['latestDescription']
                    arn = event_details['arn']
                    eventTypeCategory = event_details['eventTypeCategory']
                    eventScopeCode = event_details['eventScopeCode']

                    affected_entities = [entity['entityValue'] for entity in affected_entities_response.get('entities', [])]

                    if startTime and not startTime.tzinfo:
                        startTime = startTime.replace(tzinfo=timezone.utc)
                    if lastUpdatedTime and not lastUpdatedTime.tzinfo:
                        lastUpdatedTime = lastUpdatedTime.replace(tzinfo=timezone.utc)

                    if statusCode and statusCode.lower() not in ['closed']:
                        for entity in affected_entities:
                            aws_health_events = GaugeMetricFamily(
                                'aws_health_events',
                                'AWS Health events metrics',
                                labels=['service', 'region', 'eventTypeCode', 'statusCode', 'startTime', 'lastUpdatedTime', 'latestDescription', 'arn', 'eventTypeCategory', 'eventScopeCode', 'entity']
                            )
                            aws_health_events.add_metric(
                                [service, region, eventTypeCode, statusCode, str(startTime), str(lastUpdatedTime), latestDescription, arn, eventTypeCategory, eventScopeCode, entity],
                                1
                            )
                            yield aws_health_events

                except Exception as e:
                    syslog.syslog(syslog.LOG_ERR, f'Error al obtener detalles del evento {event_arn}: {str(e)}')

        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas de AWS HEALTH: {str(e)}')

