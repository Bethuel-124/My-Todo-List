from flask import Flask, render_template, redirect, request, jsonify, flash, Response, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, UTC
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import requests
import os
import jwt
import time
import json

load_dotenv(dotenv_path="secret.env")  # ← charge les variables d'environnement

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # ← récupère la clé



UPLOAD_FOLDER_IMG = 'static/img/assets'

#CONFIGURATION DE LA BASE DE DONNEE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sem.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()

class Compte(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail = db.Column(db.String(70))
    mot_de_passe_hash = db.Column(db.String(50))
    nom = db.Column(db.String(25))
    compte_photo = db.Column(db.String(200) , nullable = True)
    compte_nom = db.Column(db.String(25), nullable = True)
    prenom = db.Column(db.String(50))

    def __init__(self, mail, mot_de_pass, nom, prenom, compte_photo = "", compte_nom = ""):
        self.mail = mail
        self.nom = nom
        self.prenom = prenom
        self.mot_de_passe_hash = generate_password_hash(mot_de_pass)
        self.compte_photo = compte_photo
        self.compte_nom = compte_nom


    def set_password(self, mot_de_passe):
        self.mot_de_passe_hash = generate_password_hash(mot_de_passe)

    def check_password(self, mot_de_passe):
        return check_password_hash(self.mot_de_passe_hash, mot_de_passe)

class Days(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jour = db.Column(db.String(10))  # ex: "LUNDI"
    compte_id = db.Column(db.Integer, db.ForeignKey("compte.id"), nullable = False)
    remarque = db.Column(db.Text)
    rendement = db.Column(db.String(50))
    suggestion = db.Column(db.Text)
    date_enregistrement = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, jour, compte_id, remarque, rendement, suggestion, date_enregistrement):
        self.jour = jour
        self.compte_id = compte_id
        self.remarque = remarque
        self.suggestion = suggestion
        self.date_enregistrement = date_enregistrement

class Taches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jour_id = db.Column(db.Integer, db.ForeignKey("days.id"), nullable = False)
    horaire = db.Column(db.String(50))
    tache = db.Column(db.Text)
    statut = db.Column(db.String(50))

    def __init__(self, jour_id, horaire, tache, statut):
        self.jour_id = jour_id
        self.horaire = horaire
        self.tache = tache
        self.statut = statut



db.init_app(app)

#~STAY-CONNECTED
@app.route("/rester_connecte", methods = ['POST'])
def rester_connecte():
    compte = Compte.query.filter_by(id=session["user_id"]).first()
    token = jwt.encode({'user_id': compte.id}, app.config['SECRET_KEY'], algorithm = 'HS256')
    return {'token': token}




#AJOUTER DES TACHES DANS LA BD

app.secret_key = "ta_clef_secrete"






@app.route("/se_connecter", methods = ['POST'])
def se_connecter():
    data = request.get_json()
    mail = data.get('mail')
    nom = data.get("nom")
    prenom = data.get("prenom")
    mot_de_pass01 = data.get("mot_de_pass01")

    compte = Compte.query.filter_by(mail=mail).first()
    if compte and compte.check_password(mot_de_pass01):
        token = jwt.encode({'user_id': compte.id}, app.config['SECRET_KEY'], algorithm='HS256')
        session['user_id'] = compte.id  # garde la session si tu veux
        id = compte.id
        days = Days.query.filter_by(compte_id = id).all()


        taches_par_jour = {}
        for day in days:
            taches = db.session.query(Taches).filter_by(jour_id=day.id, compte_id=compte.id).all()
            taches_par_jour[day.jour] = taches

        session['user_id'] = id

        user = Compte.query.get(session['user_id'])        

        return jsonify({"token": token,
                        "nom": user.compte_nom,
                        "photo": url_for('static', filename = user.compte_photo.replace("static/", "")),
                        "taches": taches_par_jour, 
                        "message": f"Connexion réussie avec succès. Bienvenue {compte.prenom} {compte.nom}!"})

    else:
        return jsonify({"message": "Mail ou mot de passe incorrect. Veuillez réessayer ou vous inscrire."})
    

@app.route("/profile", methods = ['POST'])
def profile():
    # Récupération du texte (ex: via request.form)
    nom = request.form.get("compte_nom")

    
    # Récupération du fichier (via request.files)
    photo = request.files.get("compte_photo")

    filename = photo.filename

    if photo:

        auth_header = request.headers.get('Authorization')

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = Compte.query.filter_by(id=data["user_id"]).first()
            print("VERIOFICATION_02")
            if user:
                print("VERIOFICATION_03")
                id = user.id
                user.compte_nom = nom
                db.session.commit()

                os.makedirs(UPLOAD_FOLDER_IMG, exist_ok=True)


                nom_fichier = secure_filename(filename)
                print(nom)
                print(nom_fichier)
                chemin_photo = os.path.join(UPLOAD_FOLDER_IMG, nom_fichier)
                if os.path.exists(chemin_photo):
                    os.remove(chemin_photo)
                photo.save(os.path.join(UPLOAD_FOLDER_IMG, nom_fichier))
                user.compte_photo = f"{UPLOAD_FOLDER_IMG}/{nom_fichier}"
                db.session.commit()

                return jsonify({
                    "nom": nom,
                    "photo": url_for('static', filename = user.compte_photo.replace("static/", "")),

                })
        except jwt.ExpiredSignatureError:
            return "Token expiré", 401
        except jwt.InvalidTokenError:
            return "Token invalide", 401
    else:
        return "ERROR"

        
@app.route("/s_inscrire", methods=['POST'])
def s_inscrire():
    data = request.get_json()
    mail = data.get('mail')
    nom = data.get("nom")
    prenom = data.get("prenom")
    mot_de_pass01 = data.get("mot_de_pass01")
    mot_de_pass02 = data.get("mot_de_pass02")


    if mot_de_pass01 != mot_de_pass02:
        return jsonify({"message": "Les deux mots de passe ne sont pas identiques. Veuillez réessayer."})

    # Vérifie si un compte avec le même mail existe déjà
    compte_existant = Compte.query.filter_by(mail=mail).first()
    if compte_existant:
        return jsonify({'message': 'Vous avez déjà un compte avec ce mail. Veuillez en utiliser un autre.'})

    # Crée et enregistre le nouveau compte
    nouveau_compte = Compte(mail, mot_de_pass01, nom, prenom)
    db.session.add(nouveau_compte)
    db.session.commit()

    token = jwt.encode({'user_id': nouveau_compte.id}, app.config['SECRET_KEY'], algorithm = 'HS256')

    return jsonify({'token': token, 'message': 'Bienvenue sur BethSAkt. Votre compte a été créé avec succès. Merci !'})


def ajouter(mot_de_pass, jour, remarque, rendement, suggestion, data):

    personne  = Compte.query.filter_by(mot_de_pass = mot_de_pass)

    ident = personne.id

    nouveau_jour = Days(jour, ident, remarque, rendement,suggestion)

    instance01 = db.session.query(Days).filter(Days.compte_id == ident, Days.jour == jour).first()
    db.session.delete(instance01)
    db.session.commit()
    db.session.add(nouveau_jour)
    db.session.commit()

    instance02 = db.session.query(Taches).join(instance01)
    db.session.delete(instance02)
    db.session.commit()
    for i in data:
        jour_id = nouveau_jour.id
        horaire = i.get("horaire")
        tache = i.get("tache")
        statut = i.get("statut")
        nouvelle_tache = Taches(jour_id, horaire, tache, statut)
        db.session.add(nouvelle_tache)
        db.session.commit() 



#RECHARGER


# Ton token Hugging Face
HF_API_KEY = os.getenv("HF_API_KEY")
MODEL_URL = "https://router.huggingface.co/featherless-ai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}



def poser_question_directe(contexte, question):
    prompt = f"Voici ce de quoi il est question :\n{contexte}\n\nQuestion : {question}\nRéponds brièvement."
    
    payload = {
        "model": "Qwen/Qwen3-8B",  
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 256
    }

    response = requests.post(MODEL_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        result = response.json()
        raw_text = result["choices"][0]["message"]["content"]
        # Nettoyer <think> et autres métadonnées
        cleaned_text = raw_text.split("</think>")[-1].strip() if "</think>" in raw_text else raw_text.strip()
        return cleaned_text
    else:
        return f"Erreur HuggingFace: {response.status_code} - {response.text}"

@app.route("/programme", methods=["POST"])
def programme():
    data = request.get_json()
    tableau = data.get('tableau')
    identifiant = data.get('identifiant')

    jours = {0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi", 4: "vendredi", 5: "samedi", 6: "dimanche"}
    jour = jours.get(identifiant, "inconnu")
    contexte = str(tableau)

    message01 = poser_question_directe(contexte, "Trouve-moi une remarque sur ma journée.")
    message02 = poser_question_directe(contexte, "Quel est mon rendement (en % et adjectif comme médiocre, bien, excellent) ?")
    message03 = poser_question_directe(contexte, "Donne une suggestion pour mieux organiser mes journées.")

    return jsonify({"jour": jour, "message01": message01, "message02": message02, "message03": message03})


#CONFIGURATION DE DEEPSEEK(IA)

#from openai import OpenAI

#client = OpenAI(
#  base_url="https://openrouter.ai/api/v1",
#  api_key="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",
#)

#client = OpenAI(
#  base_url="https://openrouter.ai/api/v1",
#  api_key="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",
#)


#client = OpenAI(
#  base_url="https://openrouter.ai/api/v1",
#  api_key="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",
#)









@app.route("/")
def index():
    auth_header = request.headers.get('Authorization')

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            compte = Compte.query.filter_by(id=data["user_id"]).first()
            if compte:
                id = compte.id
                days = Days.query.filter_by(compte_id = id).all()


                taches_par_jour = {}
                for day in days:
                    taches = db.session.query(Taches).filter_by(jour_id=day.id, compte_id=compte.id).all()
                    taches_par_jour[day.jour] = taches

                session['user_id'] = id

                user = Compte.query.get(session['user_id'])        

                infos = {"nom": user.compte_nom,
                                "photo": url_for('static', filename = user.compte_photo.replace("static/", "")),
                                "taches": taches_par_jour, 
                                "message": f"Connexion réussie avec succès. Bienvenue {compte.prenom} {compte.nom}!"}
                if infos["nom"] != "":
                    return render_template("index1.html", first = False, infos = infos )
                else:
                    return render_template("index1.html", first = True)
        except jwt.ExpiredSignatureError:
            return "Token expiré", 401
        except jwt.InvalidTokenError:
            return "Token invalide", 401
    else:
        return render_template("index1.html", first = True)



if __name__ == "__main__":

# Supprimer tous les livres
#db.session.query(Livre).delete()
#db.session.commit()

#print("Tous les livres ont été supprimés.")

    #with app.app_context():
    #   db.drop_all()
    #   print("✅ Toutes les tables ont été supprimées.")
    #with app.app_context():
    #    db.create_all()
    #    print("✅ Toutes les tables ont été recréées.")

    app.run(debug=True)
