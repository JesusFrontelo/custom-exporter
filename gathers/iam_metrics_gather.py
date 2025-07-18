from prometheus_client.core import GaugeMetricFamily
from sessions import sso_session
import syslog
from datetime import datetime, timezone

class IAMMetricsCollector:
    def collect(self):
        try:
            iam_client = sso_session.iam_client
            now = datetime.now(timezone.utc)
            response = iam_client.list_users()

            for user in response['Users']:
                user_name = user['UserName']
                create_date = user['CreateDate'].isoformat()
                last_activity = None
                access_key_ages = []

                # Obtener claves de acceso y calcular edad y última actividad
                try:
                    access_keys = iam_client.list_access_keys(UserName=user_name)['AccessKeyMetadata']
                    for i, key in enumerate(access_keys):
                        key_id = key['AccessKeyId']
                        key_create_date = key['CreateDate']
                        age_days = (now - key_create_date).days
                        access_key_ages.append(age_days)

                        # Estado del Access Key
                        key_status_metric = GaugeMetricFamily(
                            'aws_iam_access_key_status',
                            'Estado de la clave de acceso IAM (1=Active, 0=Inactive)',
                            labels=['user_name', 'key_index', 'access_key_id']
                        )
                        key_status_metric.add_metric([user_name, str(i + 1), key_id], 0 if key['Status'] == 'Active' else 1)
                        yield key_status_metric

                        # Último uso de la clave
                        try:
                            last_used_info = iam_client.get_access_key_last_used(AccessKeyId=key_id)
                            last_used_date = last_used_info['AccessKeyLastUsed'].get('LastUsedDate')

                            if last_used_date:
                                seconds_since_last_used = (now - last_used_date).total_seconds()
                                key_last_used_metric = GaugeMetricFamily(
                                    'aws_iam_access_key_last_used_seconds',
                                    'Segundos desde el último uso de la clave de acceso IAM',
                                    labels=['user_name', 'access_key_id']
                                )
                                key_last_used_metric.add_metric([user_name, key_id], seconds_since_last_used)
                                yield key_last_used_metric

                                # Actualizar última actividad general del usuario
                                if not last_activity or last_used_date > last_activity:
                                    last_activity = last_used_date

                        except Exception as e:
                            syslog.syslog(syslog.LOG_WARNING, f"Error al obtener uso de clave {key_id} de {user_name}: {str(e)}")

                except Exception as e:
                    syslog.syslog(syslog.LOG_WARNING, f"Error al obtener claves de {user_name}: {str(e)}")

                # Último uso de la consola
                try:
                    user_info = iam_client.get_user(UserName=user_name)
                    password_last_used = user_info['User'].get('PasswordLastUsed')
                    if password_last_used and (not last_activity or password_last_used > last_activity):
                        last_activity = password_last_used
                except Exception as e:
                    syslog.syslog(syslog.LOG_WARNING, f"Error al obtener info de consola de {user_name}: {str(e)}")

                # Métrica: Información básica del usuario
                user_info_metric = GaugeMetricFamily(
                    'aws_iam_user_info',
                    'Información básica del usuario IAM',
                    labels=['user_name', 'create_date']
                )
                user_info_metric.add_metric([user_name, create_date], 1)
                yield user_info_metric

                # Métrica: Última actividad
                if last_activity:
                    seconds_since_last_activity = (now - last_activity).total_seconds()
                    last_activity_metric = GaugeMetricFamily(
                        'aws_iam_user_last_activity_seconds',
                        'Segundos desde la última actividad del usuario IAM',
                        labels=['user_name']
                    )
                    last_activity_metric.add_metric([user_name], seconds_since_last_activity)
                    yield last_activity_metric

                # Métrica: Edad de claves de acceso
                for i, age in enumerate(access_key_ages):
                    key_age_metric = GaugeMetricFamily(
                        'aws_iam_access_key_age_days',
                        'Edad de la clave de acceso en días',
                        labels=['user_name', 'key_index']
                    )
                    key_age_metric.add_metric([user_name, str(i + 1)], age)
                    yield key_age_metric

        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas de IAM: {str(e)}')