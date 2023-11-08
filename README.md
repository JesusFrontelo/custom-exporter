# Custom Exporter


## Description

A Prometheus Exporter for AWS, written in Python. 

This exporter tries to be an easy way to export everything from AWS as a metric. 

It´s been developed to run on an instance with instance_profile, and can assume role or use the instance_profile role, and it renews credentials automatically. 

## Installation

First of all you need python3 and install the below libraries:

- boto3
- botocore
- prometheus_client

to install these libraries you can run as follow:

````
python3 pip install <library>
````
To start gathering metrics run:
````
python3 metrics_gather.py 
````

## How to configure

### Configuring the exporter

If you plan to assume a role, you must set it as a --role argument. \
You can expose metrics on a specific port setting the --port argument, if you don't set the argument it has the default port set to 10000.

You can configure it as a linux service. An example of service configuration:

````
Description=Python exporter for Prometheus
After=network.target

[Service]
Type=simple
User=<the user which has python access and libraries>
ExecStart=/usr/bin/python3 /path/to/exporter/metrics_gather.py --role 'arn:aws:iam::123456789012:role/role_to_assume' --port 9900
Restart=on-failure

[Install]
WantedBy=multi-user.target
````

### Definiton of each file

If you plan to add new metrics to the exporter, this info is useful to know where to config each thing. 

| FILE | DESCRIPTION |
| :--: | ----------- |
|sso_session.py | It has the configuration to stablish session with aws and creates each client (ec2, rds...). |
|*_metrics_def.py | It has the definition of each metric. Here you can add new metrics definition (name of the metric, description and labels).|
|metrics_gather.py | Here we collect metrics and assign it to a metric.|