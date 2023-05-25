import requests;
import logging;

class clientUtil:
    def load_properties(file_path):
        """
        Load properties from a file.
        """
        properties = {}
        with open(file_path, 'r') as f:
            for line in f:
                if not line.startswith('#'):
                    key, value = line.strip().split('=')
                    properties[key] = value
        return properties
    
    def write_properties(file_path, key, newvalue):
        """
        Write properties to a file.
        """
        properties = {}
        with open(file_path, 'r') as f:
            for line in f:
                if not line.startswith('#'):
                    key, value = line.strip().split('=')
                    properties[key] = value
        if key in properties.keys():
            properties[key] = str(newvalue)
        else:
            properties[key] = value
        with open(file_path, 'w') as f:
            for key, value in properties.items():
                f.write(key + "=" + value)
                f.write("\n")

    # Call Rest API
    def call_api(url, payload):
        logging.info("Calling API: " + url)
        try:
            # print the curl command
            logging.info("curl -X POST -H \"Content-Type: application/json\" -d '" + str(payload) + "' " + url)
            response = requests.post(url, json=payload)        
            if response.status_code == 200:
                logging.info("API call successful")
                return True
            else:
                logging.info("API call failed")
                return False
        except Exception as e:
            logging.exception(e)
            return False