import pytest
import salesforce_events.app.PubSub as PubSub
from salesforce_events.util.ClientUtil import clientUtil

def test_auth():
    # load properties using load_properties function 
    properties = clientUtil.load_properties("./salesforce_events/resources/application.properties")
    # create a PubSub object with properties
    pubsub = PubSub.PubSub(properties)
    # call auth function
    pubsub.auth()
    # check session_id is a string
    assert isinstance(pubsub.session_id, str)
    # check session_id is not empty
    assert pubsub.session_id != ''


                     

    