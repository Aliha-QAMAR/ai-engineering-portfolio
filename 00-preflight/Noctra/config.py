import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'noctra-dev-key-change-in-production')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///noctra.db')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
