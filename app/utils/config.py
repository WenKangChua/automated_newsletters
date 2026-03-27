import yaml
from pathlib import Path
from datetime import datetime

def load_config(config_file: str) -> dict[str]:
    """
    Open a config file which contains data in yaml
    """
    config_path = Path(__file__).parent.parent / config_file
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

config = load_config("config.yaml")
base_path:Path = Path(__file__).parent.parent
datetime_now:str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    print(config)