from flask import Flask, current_app, redirect, url_for
from flask_migrate import Migrate
from extensions import db, login_manager, mail
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.clients import clients_bp
from routes.tickets import tickets_bp
from models import Utilisateur
from flask_login import login_required
import os  # 📢 ajout pour le chemin absolu

# Initialisation de l'app
app = Flask(__name__)

# Gestion sécurisée des chemins vers la base
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'super-secret-key'

# Correction ici ⬇️
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ticket.it360@gmail.com'
app.config['MAIL_PASSWORD'] = 'zdnt vydo apbg xjfu'
app.config['MAIL_DEFAULT_SENDER'] = 'ticket.it360@gmail.com'

# Initialisation des extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
mail.init_app(app)
migrate = Migrate(app, db)

# User loader
@login_manager.user_loader
def load_user(user_id):
    with current_app.app_context():
        return db.session.get(Utilisateur, int(user_id))

# Redirection racine
@app.route("/")
@login_required
def index():
    return redirect(url_for("dashboard.index"))

# Filtre custom pour l'affichage des minutes → heures:minutes
@app.template_filter()
def minutes_to_hm(value):
    try:
        heures = abs(value) // 60
        minutes = abs(value) % 60
        signe = "-" if value < 0 else ""
        return f"{signe}{heures}h{minutes:02d}"
    except:
        return "0h00"

# Enregistrement des blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(tickets_bp)

# Lancement de l'application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("✅ Application Flask lancée sur http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)

