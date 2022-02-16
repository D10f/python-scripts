from pathlib import Path

CURRENT_VERSION = '0.0.1'

PROJECT_DIR = Path(__file__).resolve().parent
VENDOR_LIST = Path.joinpath(PROJECT_DIR, 'data', 'vendors.yml')
DOCS_LIST = Path.joinpath(PROJECT_DIR, 'data', 'documentation.yml')
LANGUAGE_LIST = Path.joinpath(PROJECT_DIR, 'data', 'languages.yml')
