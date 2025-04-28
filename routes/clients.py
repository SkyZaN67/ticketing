from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Client, Contrat
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

@clients_bp.route('/')
@login_required
def index():
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)

@clients_bp.route('/<int:client_id>')
@login_required
def detail(client_id):
    client = Client.query.get_or_404(client_id)
    annee = request.args.get('annee', str(datetime.now().year))

    tickets = [ticket for ticket in client.tickets if ticket.date_creation.year == int(annee)]
    total_utilise = sum(ticket.temps_facture for ticket in tickets if ticket.temps_facture is not None)

    solde_total = client.solde_annuel.get(annee, 0)
    solde_restant = solde_total - total_utilise

    contrats = Contrat.query.all()

    return render_template('client_detail.html', client=client, annee=annee, tickets=tickets,
                           total_utilise=total_utilise, solde_total=solde_total, solde_restant=solde_restant,
                           contrats=contrats)

@clients_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        nom = request.form.get('nom')
        telephone = request.form.get('telephone')
        email = request.form.get('email')
        nouveau_client = Client(nom=nom, telephone=telephone, email=email, solde_annuel={})
        db.session.add(nouveau_client)
        db.session.commit()
        return redirect(url_for('dashboard.index'))
    return render_template('create_client.html')

@clients_bp.route('/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        client.nom = request.form.get('nom')
        client.telephone = request.form.get('telephone')
        client.email = request.form.get('email')
        db.session.commit()
        return redirect(url_for('dashboard.index'))
    return render_template('edit_client.html', client=client)

@clients_bp.route('/<int:client_id>/delete', methods=['POST'])
@login_required
def delete(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('dashboard.index'))

@clients_bp.route('/<int:client_id>/add_solde', methods=['POST'])
@login_required
def add_solde(client_id):
    client = Client.query.get_or_404(client_id)
    annee = request.form.get('annee', str(datetime.now().year))
    contrat_id = request.form.get('contrat_id')
    nouveau_solde = request.form.get('nouveau_solde')

    if not client.solde_annuel:
        client.solde_annuel = {}

    if contrat_id:
        contrat = Contrat.query.get(contrat_id)
        if contrat:
            solde_actuel = client.solde_annuel.get(annee, 0)
            client.solde_annuel[annee] = solde_actuel + int(contrat.duree * 60)
            client.contrat_id = contrat.id  # 🆕 Lier le contrat choisi
            flash(f"✅ {int(contrat.duree * 60)} minutes ajoutées avec le contrat {contrat.nom}.", "success")
    elif nouveau_solde:
        try:
            nouveau_solde = int(nouveau_solde)
            client.solde_annuel[annee] = nouveau_solde
            flash(f"✅ Solde mis à jour à {nouveau_solde} minutes.", "success")
        except ValueError:
            flash("❌ Erreur : Le solde entré est invalide.", "danger")
    else:
        flash("⚠️ Veuillez sélectionner un contrat ou entrer un nouveau solde.", "warning")

    flag_modified(client, "solde_annuel")
    db.session.commit()
    return redirect(url_for('clients.detail', client_id=client.id, annee=annee))

@clients_bp.route('/<int:client_id>/report_solde', methods=['POST'])
@login_required
def report_solde(client_id):
    client = Client.query.get_or_404(client_id)
    annee = request.form.get('annee')
    prochaine_annee = str(int(annee) + 1)

    if not client.solde_annuel:
        client.solde_annuel = {}

    total_utilise = sum(
        ticket.temps_facture for ticket in client.tickets
        if ticket.temps_facture is not None and ticket.date_creation.year == int(annee)
    )

    solde_actuel = client.solde_annuel.get(annee, 0)
    solde_restant = solde_actuel - total_utilise

    solde_suivante = client.solde_annuel.get(prochaine_annee, 0)
    client.solde_annuel[prochaine_annee] = solde_suivante + solde_restant

    flag_modified(client, "solde_annuel")
    db.session.commit()

    flash(f"✅ Solde de {solde_restant} minutes reporté sur {prochaine_annee}.", "success")
    return redirect(url_for('clients.detail', client_id=client.id, annee=prochaine_annee))

@clients_bp.route('/<int:client_id>/update_contrat', methods=['POST'])
@login_required
def update_contrat(client_id):
    client = Client.query.get_or_404(client_id)
    contrat_id = request.form.get('contrat_id')

    if contrat_id:
        client.contrat_id = contrat_id
        db.session.commit()
        flash("✅ Contrat mis à jour avec succès.", "success")
    else:
        flash("❌ Erreur : Aucun contrat sélectionné.", "danger")

    return redirect(url_for('clients.detail', client_id=client.id))
