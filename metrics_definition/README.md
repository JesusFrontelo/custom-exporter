# Metrics Definition

### Definition of each file

| FILE | DESCRIPTION |
| :--: | ----------- |
|ec2_metrics_def.py | It has the metrics definition for ec2.|
|rds_metrics_def.py | It has the metrics definition for rds.|
|elb_metrics_def.py | It has the metrics definition for elb.|

### How to define metrics

First you need to define the a name for the metric variable, in the example is (instance_state_metric). \
The you need to instrument it, defining a metric name (ec2_instance_state), summarize it with a brief description of what it get (Estado de las instancias EC2).\
Finally you must add the labels to the metric ('instance_id', 'instance_type', 'state'). These labels must be populated later in the gather file. \

Example of metric definition: 
````
instance_state_metric = Gauge(
    'ec2_instance_state', 
    'Estado de las instancias EC2', 
    ['instance_id', 'instance_type', 'state']
    )
````