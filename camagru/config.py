import os
from dotenv import load_dotenv

bool_map = {
    "true": True, "TRUE": True, "True": True,
    "false": False, "FALSE": False, "False": False
}

env_path = os.getenv("ENV_PATH") or ".env"
load_dotenv(env_path)

#Flask env
SECRET_KEY = os.getenv("SECRET_KEY", "dev")

#Misc
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

#Server config
GUNICORN_WORKERS= os.getenv("GUNICORN_WORKERS", "2")
GUNICORN_THREADS= os.getenv("GUNICORN_THREADS", "2")
GUNICORN_TIMEOUT= os.getenv("GUNICORN_TIMEOUT", "30")

#DB
DATABASE = os.getenv("DATABASE", os.path.join("instance", "camagru.sqlite"))

#Mail config
MAIL_SERVER = os.getenv("MAIL_SERVER", "mail")
MAIL_PORT = os.getenv("MAIL_PORT", "1025")
MAIL_USE_TLS = bool_map.get(os.getenv("MAIL_USE_TLS", "False"))
MAIL_USE_SSL = bool_map.get(os.getenv("MAIL_USE_SSL", "False"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "camagru")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "password123")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@camagru.test")
MAIL_MAX_EMAILS = int(os.getenv("MAIL_MAX_EMAILS", "10"))
MAIL_SUPPRESS_SEND = bool_map.get(os.getenv("MAIL_SUPPRESS_SEND", "False"))
MAIL_SENDER_NAME = os.getenv("MAIL_SENDER_NAME", "Camagru")


FLASK_ENV = os.getenv("FLASK_ENV", "dev")
if FLASK_ENV == "dev":
    DEBUG = True
    MAIL_USE_STARTTLS = False
    MAIL_DEBUG = True
if FLASK_ENV == "prod":
    DEBUG = False
    MAIL_SUPPRESS_SEND = False

