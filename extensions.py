from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail  # ✅ on importe Mail ici

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()  # ✅ on ajoute l'instance ici

