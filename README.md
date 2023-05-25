# PCA Salesforce Change Data Capture Listener

## This Python project can be used to listen to changes occurring in salesforce. These changes can be posted to a REST API.

</br>

## The main configuration file that can be used to change the behaviour of this listener is located under the resources folder known as application.properties.

</br>

``` properties
url=salesforce login url
username=username
password=password
metadata=None
grpc_host=api.pubsub.salesforce.com
grpc_port=7443
pb2=pb2
topic_name=/data/ChangeEvents
instance_url=instance url for the organization
tenant_id=organization id / tenant id
apiVersion=55.0
objects=your objects in comma separated values
apis=api's to post
subscription_type=CUSTOM or EARLIEST for subscription type
latest_replay_id=Latest replay id
```