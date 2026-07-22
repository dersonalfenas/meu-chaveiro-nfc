import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-super-secreta-123456')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///meu_chaveiro.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN', '')
    MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY', '')
    
    PLANO_MENSAL_VALOR = 19.90
    PLANO_ANUAL_VALOR = 199.00
    PLANO_MENSAL_LIMITE_TAGS = 3
    PLANO_ANUAL_LIMITE_TAGS = 10
    
    SITE_URL = os.getenv('SITE_URL', 'https://diga3dtags.onrender.com')
