from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
    db.create_all()
    # Cria admin se não existir
    admin = Usuario.query.filter_by(email='admin@admin.com').first()
    if not admin:
        admin = Usuario(nome='Admin', email='admin@admin.com', admin=True)
        admin.set_senha('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run()
