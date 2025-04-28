import csv
from app import app
from extensions import db
from models import Client

with app.app_context():
    with open('client.csv', mode='r', encoding='ISO-8859-1') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            nom = row.get('Nom')
            telephone = row.get('Téléphone fixe (facturation)', '').strip()
            if nom:
                client = Client(nom=nom.strip(), telephone=telephone if telephone else None)
                db.session.add(client)
        db.session.commit()
        print("✅ Tous les clients du fichier CSV ont été importés avec succès.")
