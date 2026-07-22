import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-secreta-muito-forte')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///meu_chaveiro.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mercado Pago
    MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')
    MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY')
    
    # Planos
    PLANO_MENSAL_VALOR = 19.90
    PLANO_ANUAL_VALOR = 199.00
    PLANO_MENSAL_LIMITE_TAGS = 3
    PLANO_ANUAL_LIMITE_TAGS = 10
    
    # URL do site
    SITE_URL = os.getenv('SITE_URL', 'http://localhost:5000')