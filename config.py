
#Variables que apuntan a la base de datos

import os
from dotenv import load_dotenv
load_dotenv()

POSTGRES = os.getenv('URL_DB_POSTGRES')

class Config:
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    SQLALCHEMY_DATABASE_URI = POSTGRES