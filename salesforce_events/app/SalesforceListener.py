"""
SalesforceListener.py

This is a subscriber client that listens for `/event/NewOrderConfirmation__e`
events published by the inventory app (`InventoryApp.py`). The `if __debug__`
conditionals are to slow down the speed of the app for demoing purposes.
"""

import os, sys, avro

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
parent_dir_path = os.path.abspath(os.path.join(parent_dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

from salesforce_events.util.ChangeEventHeaderUtility import process_bitmap
import json
import logging
import time
import salesforce_events.app.PubSub as PubSub
from salesforce_events.util.ClientUtil import clientUtil

global latest_replay_id

def process_event(event, pubsub):    
    # get latest replay id
    global latest_replay_id

    logging.info("Received event with replay id: " + str(int.from_bytes(event.latest_replay_id, byteorder='little', signed=False)))
    if event.events:
        
        if event.pending_num_requested == 0:
            pubsub.semaphore.release()

        for evt in event.events:
            payload_bytes = evt.event.payload
            json_schema = pubsub.get_schema_json(evt.event.schema_id)
            decoded_event = pubsub.decode(json_schema, payload_bytes)
            # convert decoded_event to json
            response = json.loads(json.dumps(decoded_event))
                        
            # Change the changedFields to human readable format
            if 'ChangeEventHeader' in decoded_event:
                changed_fields = decoded_event['ChangeEventHeader']['changedFields']
                changed_fields_decoded=[]
                for key in process_bitmap(avro.schema.parse(json_schema), changed_fields):
                    changed_fields_decoded.append(key)
                response['ChangeEventHeader']['changedFields'] = changed_fields_decoded
                logging.info(response)

            # Match the entity name with the object name in application.properties
            for i in range(len(properties['objects'])):
                if properties['objects'][i] == response['ChangeEventHeader']['entityName']:
                    # add latest replay id to response
                    response['latest_replay_id'] = int.from_bytes(event.latest_replay_id, byteorder='little', signed=False)
                    # Call the API
                    status = clientUtil.call_api(properties['apis'][i], response)
                    if status:
                        # onsuccess update the latest replay id for continuous processing
                        latest_replay_id = event.latest_replay_id  
                        latest_replay_id = int.from_bytes(latest_replay_id, byteorder='little', signed=False)
                        # Write the replay id to application.properties
                        clientUtil.write_properties("./salesforce_events/resources/application.properties", "latest_replay_id", latest_replay_id)
                    
    
    else:
        logging.info("Subscribtion is active but no events received yet")


def run(argument_dict):
    global latest_replay_id           
    latest_replay_id = int(argument_dict['latest_replay_id'])

    sfdc_updater = PubSub.PubSub(argument_dict)
    sfdc_updater.auth()

    if properties.get('subscription_type') == 'EARLIEST':
        logging.info("subscribing to topic: " + argument_dict['topic_name'] + " with No Replay ID")
        sfdc_updater.subscribe(argument_dict['topic_name'], "EARLIEST", '', 1, process_event)

    elif properties.get('subscription_type') == 'CUSTOM':
        replay_id_in_bytes = latest_replay_id.to_bytes(8, byteorder='little').hex()
        logging.info("subscribing to topic: " + argument_dict['topic_name'] + " with Replay ID: " + str(latest_replay_id) + "")
        sfdc_updater.subscribe(argument_dict['topic_name'], "CUSTOM", replay_id_in_bytes, 1, process_event)

    else:
        logging.info("Invalid Subscription Type")
        sys.exit()

if __name__ == '__main__':
    properties = clientUtil.load_properties("./salesforce_events/resources/application.properties")
    # Convert to list
    properties['objects'] = properties.get('objects').split(',')
    properties['apis'] = properties.get('apis').split(',')

    # Check for null value in the list
    if '' in properties['objects'] or '' in properties['apis']:
        raise Exception("Null value found in the objects or apis list")

    #  Check the length of the objects and apis list
    if len(properties['objects']) != len(properties['apis']):
        raise Exception("The number of objects and apis must be the same")
    
    # logging setup
    if properties.get('logging_level') == 'INFO':
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    elif properties.get('logging_level') == 'DEBUG':
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Starting Salesforce Listener")
    run(properties)