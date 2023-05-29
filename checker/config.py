import json
import os

class Config:
    def __init__(self, config_file):
        dirname = os.path.dirname(__file__)
        config_file = os.path.join(dirname, config_file)

        with open(config_file) as f:
            self.config = json.load(f)
        
        # Check if all required keys are present
        if not 'port' in self.config:
            raise ValueError("Port not specified in config file")
        self.port = self.config['port']