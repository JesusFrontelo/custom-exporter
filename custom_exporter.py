####################################################################################
#####                                                                          #####
#####                               Metrics Gather                             #####
#####                                                                          #####
####################################################################################

import os
import sys
import time
import syslog

from gathers import ec2_metrics_gather, rds_metrics_gather, elb_metrics_gather, health_metrics_gather
from sessions import sso_session
from prometheus_client import start_http_server, Info

## Establecemos el path del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

### Comenzamos la colecta de métricas ###

# Inicia el servidor Prometheus en el puerto especificado
start_http_server(sso_session.port)

### Definimos la versión del exporter

i = Info('custom_exporter_version', 'Info')
i.info({'version': '0.2.0', 'Author': 'Jesus Frontelo'})

while True:
    try:

        ### EC2 Metrics Gathering ###
        ec2_metrics_gather.ec2_gather()

        ### RDS Metrics Gathering ###
        rds_metrics_gather.rds_gather()

        ### ELB Metrics Gathering ###
        elb_metrics_gather.elb_gather()

        ### HEALTH Metrics Gathering ###
        health_metrics_gather.health_gather()

    except Exception as e:
       # Registra cualquier excepción que ocurra durante la obtención de métricas       
       syslog.syslog(syslog.LOG_ERR, f'Error al obtener métricas: {str(e)}')

    # Agrega un retardo (por ejemplo, 60 segundos) antes de volver a obtener los datos
    import time
    time.sleep(60)
