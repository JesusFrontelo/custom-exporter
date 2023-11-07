####################################################################################
#####                                                                          #####
#####                              PYTHON-EXPORTER                             #####
#####                                                                          #####
#####                     Creado por Jesús Frontelo Gonzálvez                  #####
#####                                                                          #####
#####                             Noviembre de 2023                            #####
#####                                                                          #####
####################################################################################

import argparse
import boto3
import subprocess

from botocore.credentials import RefreshableCredentials
from botocore.session import get_session
from datetime import datetime, timedelta, timezone
from prometheus_client import start_http_server

parser = argparse.ArgumentParser(description='Script de Sesiones')
parser.add_argument('--role', type=str, required=False, help='ARN del rol')
parser.add_argument('--port', type=int, default=10000, help='Puerto del servidor HTTP de Prometheus')
args = parser.parse_args()
role_arn = args.role
port = args.port

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

def refresh():
    #" Refresh tokens by calling assume_role again "
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

    return credentials

session_credentials = RefreshableCredentials.create_from_metadata(
    metadata=refresh(),
    refresh_using=refresh,
    method="sts-assume-role",
)

session = get_session()
session._credentials = session_credentials
session.set_config_variable("region", 'eu-west-1')
autorefresh_session = boto3.Session(botocore_session=session)

rds_client = autorefresh_session.client(
    "rds", 
    region_name='eu-west-1'
)

ec2_client = autorefresh_session.client(
    "ec2",
    region_name='eu-west-1'
)

print(response.get("Expiration").isoformat())
