import json
import traceback


DEFAULT_CONFIG = {
    "parameters": {
        "temperature": 0.7,
        "max_output_tokens": 512,
        "topK": 40,
        "topP": 0.95
    }
}


def load_config():
    try:
        with open('./config/app_config.json', 'r') as config_file:
            config = json.load(config_file)
            return config['parameters']
    except FileNotFoundError:
        print("Configuration file not found.")
    except json.JSONDecodeError:
        print("Error parsing configuration file.")
    except Exception:
        print("Unable to load config file", traceback.format_exc())

    return DEFAULT_CONFIG['parameters']


