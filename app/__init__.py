from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # Configurar o caminho absoluto para a pasta templates
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    # Importar e registrar blueprints
    from app import routes, auth
    app.register_blueprint(routes.bp)
    app.register_blueprint(auth.bp)
    
    return app
