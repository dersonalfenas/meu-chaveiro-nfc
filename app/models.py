from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20))
    empresa = db.Column(db.String(100))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    admin = db.Column(db.Boolean, default=False)
    
    tags = db.relationship('Tag', backref='usuario', lazy=True)
    assinaturas = db.relationship('Assinatura', backref='usuario', lazy=True)
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    @property
    def assinatura_ativa(self):
        assinatura = Assinatura.query.filter_by(
            usuario_id=self.id,
            pago=True
        ).order_by(Assinatura.data_fim.desc()).first()
        
        if assinatura and assinatura.data_fim > datetime.utcnow():
            return assinatura
        return None
    
    @property
    def tags_ativas(self):
        return Tag.query.filter_by(usuario_id=self.id, ativo=True).count()
    
    @property
    def limite_tags(self):
        assinatura = self.assinatura_ativa
        if not assinatura:
            return 0
        if assinatura.plano == 'mensal':
            return 3  # Plano mensal: 3 tags
        elif assinatura.plano == 'anual':
            return 10  # Plano anual: 10 tags
        return 0

class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True, nullable=False)  # ID único para NFC
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100))
    empresa = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    site = db.Column(db.String(200))
    instagram = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    foto_url = db.Column(db.String(300))
    cor_primaria = db.Column(db.String(20), default='#667eea')
    ativo = db.Column(db.Boolean, default=True)
    visualizacoes = db.Column(db.Integer, default=0)
    data_expiracao = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    def renovar(self, nova_data):
        self.data_expiracao = nova_data
        self.ativo = True
        db.session.commit()
    
    def expirou(self):
        if self.data_expiracao:
            return self.data_expiracao < datetime.utcnow()
        return False

class Assinatura(db.Model):
    __tablename__ = 'assinaturas'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    plano = db.Column(db.String(20))  # 'mensal' ou 'anual'
    valor = db.Column(db.Float)
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    pago = db.Column(db.Boolean, default=False)
    pagamento_id = db.Column(db.String(100))  # ID do pagamento no Mercado Pago
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def gerar_data_fim(self):
        if self.plano == 'mensal':
            return datetime.utcnow() + timedelta(days=30)
        elif self.plano == 'anual':
            return datetime.utcnow() + timedelta(days=365)
        return datetime.utcnow()

class ConfiguracaoSite(db.Model):
    __tablename__ = 'configuracoes'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text)