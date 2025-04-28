from app import app
from extensions import db
from models import Contrat

with app.app_context():
    contrats = [
        Contrat(nom="ATB", prix_horaire=86.0, duree_heures=8),
        Contrat(nom="ATBRONZE", prix_horaire=74.0, duree_heures=48),
        Contrat(nom="ATBRONZE+", prix_horaire=72.0, duree_heures=60),
        Contrat(nom="ATGOLD", prix_horaire=68.0, duree_heures=102),
        Contrat(nom="ATGOLD+", prix_horaire=68.0, duree_heures=120),
        Contrat(nom="ATM", prix_horaire=84.0, duree_heures=12),
        Contrat(nom="ATM+", prix_horaire=81.0, duree_heures=18),
        Contrat(nom="ATP", prix_horaire=78.0, duree_heures=24),
        Contrat(nom="ATPLATINIUM", prix_horaire=68.0, duree_heures=140),
        Contrat(nom="ATP+", prix_horaire=76.0, duree_heures=36),
        Contrat(nom="ATPRIMO", prix_horaire=89.0, duree_heures=4),
        Contrat(nom="ATSILVER", prix_horaire=70.0, duree_heures=72),
        Contrat(nom="ATSILVER+", prix_horaire=69.0, duree_heures=84),
    ]
    db.session.add_all(contrats)
    db.session.commit()
    print("✅ Tous les contrats ont été insérés en base !")
