
#Variables que apuntan a la base de datos

POSTGRES = "postgresql+psycopg://postgres:davidp23@localhost:5432/ergo_db"

class Config:
    DEBUG = True
    SECRET_KEY = 'secret_key'
    
    SQLALCHEMY_DATABASE_URI = POSTGRES