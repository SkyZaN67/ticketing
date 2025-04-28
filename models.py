from flask_login import UserMixin
from extensions import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.sqlite import JSON  # Pour stocker le solde annuel
import pytz
import math

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    telephone = db.Column(db.String(50))
    solde_annuel = db.Column(JSON, default=dict)  # Ex: {"2025": 240}
    contrat_id = db.Column(db.Integer, db.ForeignKey('contrat.id', name="fk_client_contrat_id"), nullable=True)
    contrat = db.Column(db.Boolean, default=False)
    tickets = db.relationship('Ticket', backref='client', lazy=True)

    @property
    def annee_courante(self):
        """Année en cours sous forme de string"""
        return str(datetime.now().year)

    @property
    def solde_courant(self):
        """Solde total de l'année courante"""
        return self.solde_annuel.get(self.annee_courante, 0)

    @property
    def solde_utilise(self):
        """Somme du temps facturé pour l'année en cours"""
        annee = int(self.annee_courante)
        return sum([
            ticket.temps_facture for ticket in self.tickets
            if ticket.temps_facture is not None and ticket.date_creation.year == annee
        ])

    @property
    def solde_restant(self):
        """Solde restant après consommation"""
        return self.solde_courant - self.solde_utilise

class Utilisateur(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    tickets = db.relationship('Ticket', backref='utilisateur', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    statut = db.Column(db.String(50), default='En attente')
    temps_passe_personnalise = db.Column(db.Integer, nullable=True)
    temps_facture_personnalise = db.Column(db.Integer, nullable=True)
    date_creation = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone("Europe/Paris")))
    date_debut = db.Column(db.DateTime, nullable=True)
    date_fin = db.Column(db.DateTime, nullable=True)
    rapport = db.Column(db.Text)
    demandeur = db.Column(db.String(100))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))
    urgence = db.Column(db.String(20), default='Normal')
    groupe_assignation = db.Column(db.String(50), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    observation = db.Column(db.Text, nullable=True)
    materiel_fourni = db.Column(db.Boolean, default=False)


    @hybrid_property
    def temps_passe(self):
        """Temps passé en minutes"""
        if self.temps_passe_personnalise is not None:
            return self.temps_passe_personnalise
        if self.date_debut and self.date_fin:
            delta = self.date_fin - self.date_debut
            return round(delta.total_seconds() / 60)
        return 0

    @hybrid_property
    def temps_facture(self):
        """Temps facturé en arrondissant au quart d'heure supérieur"""
        if self.temps_facture_personnalise is not None:
            return self.temps_facture_personnalise
        return math.ceil(self.temps_passe / 15) * 15 if self.temps_passe else 0

class Contrat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    prix_horaire = db.Column(db.Float, nullable=False, default=70.0)

    @property
    def duree(self):
        """Durée fixe en fonction du type de contrat"""
        durees = {
            "ATB": 8, "ATBRONZE": 48, "ATBRONZE+": 60, "ATGOLD": 102, "ATGOLD+": 120,
            "ATM": 12, "ATM+": 18, "ATP": 24, "ATPLATINIUM": 140, "ATP+": 36,
            "ATPRIMO": 4, "ATSILVER": 72, "ATSILVER+": 84,
        }
        return durees.get(self.nom, 0)

    @property
    def prix_total(self):
        """Prix total calculé: durée * prix horaire"""
        return round(self.duree * self.prix_horaire, 2)

