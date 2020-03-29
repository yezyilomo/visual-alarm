import os
import json
from pathlib import Path


HOME_DIR = Path.home()
APP_DIR = HOME_DIR.joinpath('visual-alarm')
CONFIG_FILE = APP_DIR.joinpath('config.json')

def initiate():
    if not Path.is_dir(APP_DIR):
        os.mkdir(APP_DIR)

    if not Path.is_file(CONFIG_FILE):
        config = '{"alarms": []}'
        # config file format
        # {
        # "alarms": [
        #     {
        #         "date": [year, month, day],
        #         "time": [hour, minute],
        #         "repeat": [1,2,3,4,5,6,7],  # for Mon, Tue, Wed, Thu, Fri, Sat, Sun respectively
        #         "snooze_time": 5,
        #         "snooze_number": 2
        #     }
        # ]
        # }

        with open(CONFIG_FILE, 'w') as config_file:
            config_file.write(config)

def read():
    with open(CONFIG_FILE, 'r') as config_file:
        config = config_file.read()
        return json.loads(config)

def write(config):
    with open(CONFIG_FILE, 'w') as config_file:
        config_file.write(json.dumps(config))