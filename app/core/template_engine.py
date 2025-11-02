from jinja2 import Environment, FileSystemLoader
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
template_path = BASE_DIR / "app" / "templates"
env = Environment(loader=FileSystemLoader(template_path))