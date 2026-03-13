import yaml
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

if __name__ == "__main__":
    print(config["input"]["input_pdf_path"])