import json
import os

class Config:
    def __init__(self, config_file):
        dirname = os.path.dirname(__file__)
        config_file = os.path.join(dirname, config_file)

        with open(config_file) as f:
            self.config = json.load(f)
        
        # Check if all required keys are present
        if not 'Port' in self.config:
            raise ValueError("Port not specified in config file")

        if not 'Minio' in self.config:
            raise ValueError("Minio not specified in config file")

        if not 'Environment' in self.config:
            raise ValueError("Environment not specified in config file")

        if not 'SandboxContainer' in self.config:
            raise ValueError("SandboxContainer not specified in config file")

        self.port = self.config['Port']
        self.environment = self.config['Environment']
        self.sandbox_container = self.config['SandboxContainer']

    def get(self, key):
        return self.config[key]

    def is_development(self):
        return self.environment == "Development"
    
    def is_production(self):
        return self.environment == "Production"