from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import os

# ==================== CONFIGURAÇÃO ====================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-super-secreta-123456')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///nfc_connect.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# ==================== MODELOS ====================
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20))
    empresa = db.Column(db.String(100))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    admin = db.Column(db.Boolean, default=False)
    
    tags = db.relationship('Tag', backref='dono', lazy=True)
    assinaturas = db.relationship('Assinatura', backref='dono', lazy=True)
    
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
            return 1
        if assinatura.plano == 'mensal':
            return 3
        elif assinatura.plano == 'anual':
            return 10
        return 1

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100))
    empresa = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    site = db.Column(db.String(200))
    instagram = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    cor_primaria = db.Column(db.String(20), default='#667eea')
    ativo = db.Column(db.Boolean, default=True)
    visualizacoes = db.Column(db.Integer, default=0)
    data_expiracao = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class Assinatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    plano = db.Column(db.String(20))
    valor = db.Column(db.Float)
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    pago = db.Column(db.Boolean, default=False)
    pagamento_id = db.Column(db.String(100))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def gerar_data_fim(self):
        if self.plano == 'mensal':
            return datetime.utcnow() + timedelta(days=30)
        elif self.plano == 'anual':
            return datetime.utcnow() + timedelta(days=365)
        return datetime.utcnow() + timedelta(days=30)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ==================== ROTAS PÚBLICAS ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tag/<uid>')
def visualizar_tag(uid):
    tag = Tag.query.filter_by(uid=uid, ativo=True).first()
    if not tag:
        return render_template('tag_expirada.html'), 404
    if tag.data_expiracao and tag.data_expiracao < datetime.utcnow():
        tag.ativo = False
        db.session.commit()
        return render_template('tag_expirada.html'), 403
    tag.visualizacoes += 1
    db.session.commit()
    return render_template('perfil_publico.html', tag=tag)

@app.route('/planos')
def planos():
    return render_template('planos.html')

# ==================== AUTENTICAÇÃO ====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            return redirect(url_for('dashboard'))
        flash('Email ou senha inválidos!', 'danger')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado!', 'danger')
            return render_template('registro.html')
        novo_usuario = Usuario(nome=nome, email=email)
        novo_usuario.set_senha(senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ==================== DASHBOARD ====================
@app.route('/dashboard')
@login_required
def dashboard():
    tags = Tag.query.filter_by(usuario_id=current_user.id).all()
    assinatura = current_user.assinatura_ativa
    return render_template('dashboard.html', tags=tags, assinatura=assinatura)

@app.route('/criar_tag', methods=['GET', 'POST'])
@login_required
def criar_tag():
    if request.method == 'POST':
        limite = current_user.limite_tags
        tags_ativas = current_user.tags_ativas
        if tags_ativas >= limite:
            flash('Você atingiu o limite de tags do seu plano!', 'danger')
            return redirect(url_for('planos'))
        if not current_user.assinatura_ativa:
            flash('Você precisa de uma assinatura ativa!', 'danger')
            return redirect(url_for('planos'))
        
        uid = str(uuid.uuid4()).replace('-', '')[:16]
        nova_tag = Tag(
            uid=uid,
            nome=request.form.get('nome'),
            cargo=request.form.get('cargo'),
            empresa=request.form.get('empresa'),
            telefone=request.form.get('telefone'),
            email=request.form.get('email'),
            site=request.form.get('site'),
            instagram=request.form.get('instagram'),
            linkedin=request.form.get('linkedin'),
            whatsapp=request.form.get('whatsapp'),
            cor_primaria=request.form.get('cor_primaria', '#667eea'),
            usuario_id=current_user.id,
            ativo=True,
            data_expiracao=current_user.assinatura_ativa.data_fim
        )
        db.session.add(nova_tag)
        db.session.commit()
        flash(f'Tag criada com sucesso! URL: {request.host_url}tag/{uid}', 'success')
        return redirect(url_for('dashboard'))
    return render_template('criar_tag.html')

@app.route('/editar_tag/<int:tag_id>', methods=['GET', 'POST'])
@login_required
def editar_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if tag.usuario_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        tag.nome = request.form.get('nome')
        tag.cargo = request.form.get('cargo')
        tag.empresa = request.form.get('empresa')
        tag.telefone = request.form.get('telefone')
        tag.email = request.form.get('email')
        tag.site = request.form.get('site')
        tag.instagram = request.form.get('instagram')
        tag.linkedin = request.form.get('linkedin')
        tag.whatsapp = request.form.get('whatsapp')
        tag.cor_primaria = request.form.get('cor_primaria', '#667eea')
        db.session.commit()
        flash('Tag atualizada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('editar_tag.html', tag=tag)

@app.route('/deletar_tag/<int:tag_id>', methods=['POST'])
@login_required
def deletar_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if tag.usuario_id != current_user.id:
        abort(403)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag removida com sucesso!', 'success')
    return redirect(url_for('dashboard'))

# ==================== CHECKOUT ====================
@app.route('/checkout/<plano>')
@login_required
def checkout(plano):
    if plano not in ['mensal', 'anual']:
        flash('Plano inválido!', 'danger')
        return redirect(url_for('planos'))
    assinatura = Assinatura(
        usuario_id=current_user.id,
        plano=plano,
        valor=19.90 if plano == 'mensal' else 199.00,
        data_inicio=datetime.utcnow(),
        pago=False
    )
    assinatura.data_fim = assinatura.gerar_data_fim()
    db.session.add(assinatura)
    db.session.commit()
    return render_template('pagamento.html', assinatura=assinatura, plano=plano)

# ==================== CRIAÇÃO DO BANCO E ADMIN ====================
with app.app_context():
    db.create_all()
    admin = Usuario.query.filter_by(email='admin@admin.com').first()
    if not admin:
        admin = Usuario(nome='Administrador', email='admin@admin.com', admin=True)
        admin.set_senha('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin criado: admin@admin.com / senha: admin123')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)