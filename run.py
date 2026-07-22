from app import create_app, db
from app.models import Usuario, Tag, Assinatura

app = create_app()

with app.app_context():
    db.create_all()
    
    # Criar usuário admin se não existir
    admin = Usuario.query.filter_by(email='admin@admin.com').first()
    if not admin:
        admin = Usuario(
            nome='Administrador',
            email='admin@admin.com',
            admin=True
        )
        admin.set_senha('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin criado: admin@admin.com / senha: admin123')
    
    print('✅ Banco de dados configurado com sucesso!')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)