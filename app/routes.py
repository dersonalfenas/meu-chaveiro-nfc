from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Tag, Assinatura
from datetime import datetime, timedelta
import uuid

# Criar o Blueprint para as rotas principais
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/tag/<uid>')
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

@bp.route('/planos')
def planos():
    return render_template('planos.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    tags = Tag.query.filter_by(usuario_id=current_user.id).all()
    assinatura = current_user.assinatura_ativa
    return render_template('dashboard.html', tags=tags, assinatura=assinatura)

@bp.route('/criar_tag', methods=['GET', 'POST'])
@login_required
def criar_tag():
    if request.method == 'POST':
        limite = current_user.limite_tags
        tags_ativas = current_user.tags_ativas
        
        if tags_ativas >= limite:
            flash('Você atingiu o limite de tags do seu plano!', 'danger')
            return redirect(url_for('main.planos'))
        
        if not current_user.assinatura_ativa:
            flash('Você precisa de uma assinatura ativa!', 'danger')
            return redirect(url_for('main.planos'))
        
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
        return redirect(url_for('main.dashboard'))
    
    return render_template('criar_tag.html')

@bp.route('/editar_tag/<int:tag_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.dashboard'))
    
    return render_template('editar_tag.html', tag=tag)

@bp.route('/deletar_tag/<int:tag_id>', methods=['POST'])
@login_required
def deletar_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    
    if tag.usuario_id != current_user.id:
        abort(403)
    
    db.session.delete(tag)
    db.session.commit()
    
    flash('Tag removida com sucesso!', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/checkout/<plano>')
@login_required
def checkout(plano):
    if plano not in ['mensal', 'anual']:
        flash('Plano inválido!', 'danger')
        return redirect(url_for('main.planos'))
    
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
