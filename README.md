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
python3 custom_exporter.py 
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
ExecStart=/usr/bin/python3 /path/to/exporter/custom_exporter.py --role 'arn:aws:iam::123456789012:role/role_to_assume' --port 9900
Restart=on-failure

[Install]
WantedBy=multi-user.target
````

Once you have it running you can create a job in prometheus.yml. 

````
  - job_name: '<Job Name>'
    scrape_interval: 1m
    static_configs:
      - targets: ['localhost:<Port>']

````

### Definiton of each file

If you plan to add new metrics to the exporter, this info is useful to know where to config each thing.

The first step is to define the metric at metrics_definition folder.

For metrics definition go [here](./metrics_definition/)

Then you need to set values to the metric and for each label of the metric. You can set this at gathers folder.

To set values to metric and labels go [here](./gathers/)