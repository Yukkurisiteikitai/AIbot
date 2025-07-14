# Configuration loader
from yaml import safe_load


class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as file:
            return safe_load(file)



    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            safe_load(file, self.config)


with open('cli/config/config.yaml', 'r') as file:
    config = safe_load(file)
    print(config)
