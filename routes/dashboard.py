from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Client, Ticket, Utilisateur
from sqlalchemy import or_, func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# 📑 Liste fixe des contrats
CONTRATS_FIXES = [
    {"id": 1, "nom": "ATB", "duree": 8},
    {"id": 2, "nom": "ATBRONZE", "duree": 48},
    {"id": 3, "nom": "ATBRONZE+", "duree": 60},
    {"id": 4, "nom": "ATGOLD", "duree": 102},
    {"id": 5, "nom": "ATGOLD+", "duree": 120},
    {"id": 6, "nom": "ATM", "duree": 12},
    {"id": 7, "nom": "ATM+", "duree": 18},
    {"id": 8, "nom": "ATP", "duree": 24},
    {"id": 9, "nom": "ATPLATINIUM", "duree": 140},
    {"id": 10, "nom": "ATP+", "duree": 36},
    {"id": 11, "nom": "ATPRIMO", "duree": 4},
    {"id": 12, "nom": "ATSILVER", "duree": 72},
    {"id": 13, "nom": "ATSILVER+", "duree": 84},
]

@dashboard_bp.route('/')
@login_required
def index():
    filtre_statut = request.args.get('statut')

    if current_user.role == 'technicien':
        perso_query = Ticket.query.filter(Ticket.utilisateur_id == current_user.id)
        support_query = Ticket.query.filter(
            Ticket.groupe_assignation == 'support',
            Ticket.utilisateur_id == None
        )
        en_cours_query = Ticket.query.filter(
            or_(
                Ticket.statut == 'En cours',
                Ticket.statut == 'En attente'
            ),
            or_(
                Ticket.utilisateur_id == current_user.id,
                Ticket.groupe_assignation == 'support'
            )
        )

        if filtre_statut:
            perso_query = perso_query.filter_by(statut=filtre_statut)
            support_query = support_query.filter_by(statut=filtre_statut)

        tickets_perso = perso_query.order_by(Ticket.date_creation.desc()).all()
        tickets_support = support_query.order_by(Ticket.date_creation.desc()).all()
        tickets_en_cours = en_cours_query.order_by(Ticket.date_creation.desc()).all()

        return render_template(
            'dashboard_tickets_technicien.html',
            tickets_perso=tickets_perso,
            tickets_support=tickets_support,
            tickets_en_cours=tickets_en_cours,
            filtre_statut=filtre_statut
        )
    else:
        clients = Client.query.all()
        return render_template('dashboard_clients.html', clients=clients)

# 🧩 Route pour MES CLIENTS
@dashboard_bp.route('/clients')
@login_required
def clients():
    clients = Client.query.all()
    return render_template('dashboard_clients.html', clients=clients)

# 🧩 Route pour CONTRATS
@dashboard_bp.route('/contrats', methods=['GET', 'POST'])
@login_required
def contrats():
    if 'prix_horaires' not in session:
        session['prix_horaires'] = {}

    if request.method == 'POST':
        for contrat in CONTRATS_FIXES:
            field_name = f"prix_horaire_{contrat['id']}"
            if field_name in request.form:
                try:
                    prix = float(request.form.get(field_name))
                    session['prix_horaires'][str(contrat['id'])] = prix
                except ValueError:
                    pass
        session.modified = True
        flash("✅ Prix horaires mis à jour avec succès !", "success")
        return redirect(url_for('dashboard.contrats'))

    contrats = []
    for contrat in CONTRATS_FIXES:
        prix_horaire = session['prix_horaires'].get(str(contrat['id']), 100.0)  # Prix par défaut 100€
        prix_total = round(prix_horaire * contrat['duree'], 2)
        contrats.append({
            "id": contrat['id'],
            "nom": contrat['nom'],
            "duree": contrat['duree'],
            "prix_horaire": prix_horaire,
            "prix_total": prix_total
        })

    return render_template('dashboard_contrats.html', contrats=contrats)

# 🧩 Route pour STATS
@dashboard_bp.route('/stats')
@login_required
def stats():
    periode = request.args.get('periode', '7jours')
    now = datetime.now()

    if periode == '7jours':
        date_min = now - timedelta(days=7)
        date_max = now
    elif periode == 'mois_dernier':
        premier_jour_mois = now.replace(day=1)
        date_max = premier_jour_mois - timedelta(days=1)
        date_min = date_max.replace(day=1)
    else:
        date_min = datetime(2000, 1, 1)
        date_max = now

    statut_counts = {
        'En attente': Ticket.query.filter(Ticket.statut == 'En attente', Ticket.date_creation.between(date_min, date_max)).count(),
        'En cours': Ticket.query.filter(Ticket.statut == 'En cours', Ticket.date_creation.between(date_min, date_max)).count(),
        'Terminé': Ticket.query.filter(Ticket.statut == 'Terminé', Ticket.date_creation.between(date_min, date_max)).count(),
    }

    top_intervenants = (
        Ticket.query
        .join(Utilisateur, Utilisateur.id == Ticket.utilisateur_id)
        .with_entities(Utilisateur.nom, func.count(Ticket.id))
        .filter(Ticket.date_creation.between(date_min, date_max))
        .group_by(Utilisateur.nom)
        .order_by(func.count(Ticket.id).desc())
        .limit(5)
        .all()
    )

    tickets_par_mois = (
        Ticket.query
        .with_entities(func.strftime('%Y-%m', Ticket.date_creation), func.count(Ticket.id))
        .filter(Ticket.date_creation.between(date_min, date_max))
        .group_by(func.strftime('%Y-%m', Ticket.date_creation))
        .order_by(func.strftime('%Y-%m', Ticket.date_creation))
        .all()
    )

    temps_moyen_intervenants = (
        Ticket.query
        .join(Utilisateur, Utilisateur.id == Ticket.utilisateur_id)
        .with_entities(Utilisateur.nom, func.avg(Ticket.temps_passe))
        .filter(Ticket.statut == 'Terminé', Ticket.date_creation.between(date_min, date_max))
        .group_by(Utilisateur.nom)
        .order_by(func.avg(Ticket.temps_passe))
        .limit(5)
        .all()
    )

    tickets_par_client = (
        Ticket.query
        .join(Client, Client.id == Ticket.client_id)
        .with_entities(Client.nom, func.count(Ticket.id))
        .filter(Ticket.date_creation.between(date_min, date_max))
        .group_by(Client.nom)
        .order_by(func.count(Ticket.id).desc())
        .limit(5)
        .all()
    )

    temps_passe_facture = (
        Ticket.query
        .join(Utilisateur, Utilisateur.id == Ticket.utilisateur_id)
        .with_entities(
            Utilisateur.nom,
            func.sum(Ticket.temps_passe),
            func.sum(Ticket.temps_facture)
        )
        .filter(Ticket.date_creation.between(date_min, date_max))
        .group_by(Utilisateur.nom)
        .all()
    )

    temps_passe_intervenants = {row[0]: row[1] or 0 for row in temps_passe_facture}
    temps_facture_intervenants = {row[0]: row[2] or 0 for row in temps_passe_facture}

    return render_template(
        'dashboard_stats.html',
        statut_counts=statut_counts,
        top_intervenants=top_intervenants,
        tickets_par_mois=tickets_par_mois,
        temps_moyen_intervenants=temps_moyen_intervenants,
        tickets_par_client=tickets_par_client,
        temps_passe_intervenants=temps_passe_intervenants,
        temps_facture_intervenants=temps_facture_intervenants,
        periode=periode
    )

# 🧩 Route pour TICKETS
@dashboard_bp.route('/tickets')
@login_required
def tickets():
    filtre_statut = request.args.get('statut')
    filtre_client = request.args.get('client')
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')

    if current_user.role == 'admin':
        query = Ticket.query
    else:
        query = Ticket.query.filter(Ticket.utilisateur_id == current_user.id)

    if filtre_statut:
        query = query.filter(Ticket.statut == filtre_statut)
    if filtre_client:
        query = query.join(Client).filter(Client.nom.ilike(f"%{filtre_client}%"))
    if date_debut and date_fin:
        try:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d')
            query = query.filter(Ticket.date_creation.between(date_debut_obj, date_fin_obj))
        except ValueError:
            pass

    tickets = query.order_by(Ticket.date_creation.desc()).all()

    if current_user.role == 'admin':
        return render_template(
            'dashboard_tickets_admin.html',
            tickets=tickets,
            filtre_statut=filtre_statut,
            filtre_client=filtre_client,
            date_debut=date_debut,
            date_fin=date_fin
        )
    else:
        return render_template(
            'dashboard_tickets_technicien.html',
            tickets_perso=tickets,
            tickets_support=[],
            tickets_en_cours=[],
            filtre_statut=filtre_statut
        )
