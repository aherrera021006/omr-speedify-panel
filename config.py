import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'cambia_esto_por_una_clave_segura')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://omr_user:omr_pass@localhost/omr_panel')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
