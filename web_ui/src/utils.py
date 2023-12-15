import yaml
from pathlib import Path


def load_config(project_path: Path):
    path = project_path / "config.yml"
    with open(path, "rt") as file:
        data = yaml.load(file, yaml.SafeLoader)
    return data
