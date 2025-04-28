from app import app
from extensions import db
from models import Utilisateur
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = Utilisateur(
        nom="Vincent",
        email="v.rey@it360.fr",
        mot_de_passe=generate_password_hash("Vincent2025!"),
        role="admin"
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin créé avec succès ! Email : v.rey@it360.fr / MDP : Vincent2025!")
