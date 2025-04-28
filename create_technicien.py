from app import app
from extensions import db
from models import Utilisateur
from werkzeug.security import generate_password_hash

with app.app_context():
    corentin = Utilisateur(
        nom="Fabien",
        email="f.sauvage@is2s-st.com",
        mot_de_passe=generate_password_hash("Fabien2025!"),
        role="technicien"
    )
    db.session.add(corentin)
    db.session.commit()
    print("✅ Technicien Fabien ajouté avec succès ! Email : f.sauvage@is2s-st.com | MDP : Fabien2025!")
