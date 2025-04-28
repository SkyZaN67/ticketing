import unicodedata
from app import app, db
from models import Client

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'  # ou le bon chemin

with app.app_context():
    clients = Client.query.all()
    for c in clients:
        c.solde_minutes = 0
    db.session.commit()
    print("✅ Tous les clients ont maintenant 0 minute de solde.")
print("📂 BDD utilisée :", app.config['SQLALCHEMY_DATABASE_URI'])
