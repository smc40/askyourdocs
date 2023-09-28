import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = 'static'

# load .env file
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

APP_VERSION = os.environ.get('AYD_APP_VERSION', None)

CORS_ORIGINS = ['http://localhost:3000']
