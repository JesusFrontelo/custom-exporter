import os
import sys
import syslog
import time

from sessions import sso_session

from prometheus_client import start_http_server, Info
from prometheus_client.core import REGISTRY

from gathers.rds_metrics_gather import RDSMetricsCollector
from gathers.health_metrics_gather import HealthMetricsCollector
from gathers.ec2_metrics_gather import EC2MetricsCollector
#from gathers.elb_metrics_gather import ELBMetricsCollector

# Establecemos el path del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Registrar el colector personalizado

try:
    ## Colector eventos AWS Health
    REGISTRY.register(HealthMetricsCollector())

    ## Colector EC2
    REGISTRY.register(EC2MetricsCollector())

    ## Colector RDS
    REGISTRY.register(RDSMetricsCollector())

    ## Colector ELB
#    REGISTRY.register(ELBMetricsCollector())

except Exception as e:
    syslog.syslog(syslog.LOG_ERR, f'Error al registrar colectores: {str(e)}')
    print(f'Error al registrar colectores: {str(e)}')  # Imprime el error en la consola para depuración
    sys.exit(1)  # Termina el programa si no se pueden registrar los colectores

# Inicia el servidor Prometheus en el puerto especificado
print("Iniciando el servidor Prometheus en el puerto", sso_session.port)
start_http_server(sso_session.port)

# Definimos la versión del exporter
i = Info('custom_exporter_version', 'Info')
i.info({'version': '1.0.0', 'Author': 'Jesus Frontelo'})

# Mantén el script en ejecución
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("Interrumpido por el usuario")
