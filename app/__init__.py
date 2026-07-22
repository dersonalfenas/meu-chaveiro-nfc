from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

# Criar as instâncias fora da função
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensões com o app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    # Importar e registrar blueprints
    from app import routes, auth
    app.register_blueprint(routes.bp)
    app.register_blueprint(auth.bp)
    
    return app
