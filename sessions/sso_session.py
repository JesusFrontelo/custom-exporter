####################################################################################
#####                                                                          #####
#####                              CUSTOM-EXPORTER                             #####
#####                                                                          #####
#####                     Creado por Jesús Frontelo Gonzálvez                  #####
#####                                                                          #####
#####                             Noviembre de 2023                            #####
#####                                                                          #####
####################################################################################

import argparse
import boto3
import syslog

from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

parser = argparse.ArgumentParser(description='Script de Sesiones')
parser.add_argument('--role', type=str, required=False, help='ARN del rol')
parser.add_argument('--port', type=int, default=10000, help='Puerto del servidor HTTP de Prometheus')
args = parser.parse_args()
role_arn = args.role
port = args.port

def refresh():

    try:

        # Refresh tokens by calling assume_role again
        params = {
            "RoleArn": role_arn,
            "RoleSessionName": 'my-session',
            "DurationSeconds": 3600,
        }

        #response = self.sts_client.assume_role(**params).get("Credentials")
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='my-session',
        ).get("Credentials")

        credentials = {
            "access_key": response.get("AccessKeyId"),
            "secret_key": response.get("SecretAccessKey"),
            "token": response.get("SessionToken"),
            "expiry_time": response.get("Expiration").isoformat(),
        }

        syslog.syslog(syslog.LOG_INFO, 'Session Tokens succesfully updated')
        return credentials

    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, f'Error while updating Session Tokens: {str(e)}')

# Iniciar el registro del sistema
syslog.openlog(ident='custom_exporter', logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL0)

if role_arn:
    try:
        syslog.syslog(syslog.LOG_INFO, 'Openning conection boto3 STS')
        sts_client = boto3.client("sts", region_name='eu-west-1')

        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='my-session',
        ).get("Credentials")

        metadata = {
            "access_key": response.get("AccessKeyId"),
            "secret_key": response.get("SecretAccessKey"),
            "token": response.get("SessionToken"),
            "expiry_time": response.get("Expiration").isoformat(),
        }

        syslog.syslog(syslog.LOG_INFO, 'STS Conecction success')
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, f'Error stablishing STS connection: {str(e)}')


    session_credentials = RefreshableCredentials.create_from_metadata(
        metadata=refresh(),
        refresh_using=refresh,
        method="sts-assume-role",
    )

    session = get_session()
    session._credentials = session_credentials
    session.set_config_variable("region", 'eu-west-1')
    autorefresh_session = boto3.Session(botocore_session=session)

    rds_client = autorefresh_session.client("rds",region_name='eu-west-1')
    ec2_client = autorefresh_session.client("ec2",region_name='eu-west-1')
    elb_client = autorefresh_session.client("elbv2",region_name='eu-west-1')
    cloudwatch_client = autorefresh_session.client("cloudwatch",region_name='eu-west-1')
    health_client = autorefresh_session.client("health",region_name='us-east-1')

else:
    # Utilizar las credenciales del perfil de instancia directamente
    syslog.syslog(syslog.LOG_INFO, 'Using instance profile credentials directly')
    autorefresh_session = boto3.Session()

    # Ejemplos de creación de clientes de Boto3 que no necesitan refresco de credenciales
    rds_client = boto3.client("rds", region_name='eu-west-1')
    ec2_client = boto3.client("ec2", region_name='eu-west-1')
    elb_client = boto3.client("elbv2", region_name='eu-west-1')
    cloudwatch_client = boto3.client("cloudwatch", region_name='eu-west-1')
    health_client = boto3.client("health",region_name='us-east-1')
