import json
import uuid
from typing import Dict, Any
from flask import Blueprint, jsonify, request, current_app
from moteur.moteur_eligibilite import MoteurEligibilite, Profil, flatten_keys
from utils.form_cleaner import clean_form_data
# from utils.helpers import flatten_keys  # Assurez-vous que cette fonction est définie
# from utils.constants import JSON_PATH  # Chemin vers le fichier questions.json

# Chemin relatif vers le fichier questions.json
NAT_JSON_PATH = "schemas/question_nat.json"
TITLE_JSON_PATH = "schemas/question_titre.json"

# Création du Blueprint pour l'API
api_eligibility = Blueprint("api", __name__)

with open('./schemas/new/documents_with_codes.json', 'r', encoding='utf-8') as f:
    documents_data = json.load(f)

with open('./schemas/new/required_documents_with_codes.json', 'r', encoding='utf-8') as f:
    procedures_data = json.load(f)

with open('./schemas/new/procedures.json', 'r', encoding='utf-8') as f:
    procedure_names_data = json.load(f)

# Créer un dictionnaire pour mapper les codes de documents à leurs descriptions
doc_map = {doc['code']: doc['description'] for doc in documents_data['documents']}

# Créer un dictionnaire pour mapper les identifiants de procédures aux documents requis
proc_doc_map = {proc['id']: proc['required_documents'] for proc in procedures_data['procedures']}

# Créer un dictionnaire pour mapper les identifiants de procédures à leurs noms
proc_name_map = {proc['id']: proc['name'] for proc in procedure_names_data['procedures']}


# Stockage en mémoire pour les profils (thread-safe grâce au GIL)
PROFILES: Dict[str, Dict[str, Any]] = {}

###############################################################################
# 1) Catalogue des questions
###############################################################################
@api_eligibility.route("/questions", methods=["GET"])
def questions():
    """Renvoie le JSON de configuration du questionnaire."""
    question_type = request.args.get('type', 'all')  # Default to 'all' if no type specified
    
    try:
        if question_type == "nationality_sim":
            with open(NAT_JSON_PATH, "r", encoding="utf-8") as f:
                questions_data = json.load(f)
            return jsonify(questions_data), 200
        elif question_type == "title":
            with open(TITLE_JSON_PATH, "r", encoding="utf-8") as f:
                questions_data = json.load(f)
            return jsonify(questions_data), 200
        else:
            questions_data = {}
            with open(NAT_JSON_PATH, "r", encoding="utf-8") as f:
                nat_questions = json.load(f)
                questions_data['nationality_sim'] = nat_questions
                
            with open(TITLE_JSON_PATH, "r", encoding="utf-8") as f:
                title_question = json.load(f)
                questions_data['title'] = title_question
            
            return jsonify(questions_data), 200
        
    except FileNotFoundError:
        return jsonify({"error": "Fichier questions.json introuvable"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Erreur de format dans questions.json"}), 500

###############################################################################
# 2) Calcul stateless immédiat
###############################################################################
@api_eligibility.route("/eligibilite", methods=["POST"])
def eligibilite_direct():
    """Reçoit un dict de réponses, renvoie la liste des titres."""
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"error": "Format JSON attendu"}), 400

    # Aplatir les clés et calculer l'éligibilité
    answers = flatten_keys(payload)
    answers = clean_form_data(answers)
    
    print(f"\n\n {answers} \n\n")
    results = calculer_eligibilite(answers)
    print(f"results: {results}")  # Debugging output
    return jsonify({"results": results}), 200


@api_eligibility.route("/eligibilite/<string:id>/docs", methods=["GET"])
def get_documents(id: str):
    """Renvoie les documents requis pour une procédure donnée."""
    if id not in proc_doc_map:
        return jsonify({"error": "Procédure introuvable"}), 404

    required_docs = proc_doc_map[id]
    documents = [{"code": code, "description": doc_map[code]} for code in required_docs if code in doc_map]
    
    return jsonify({"procedure_id": id, "documents": documents}), 200

###############################################################################
# 3) Création d’un profil
###############################################################################
@api_eligibility.route("/profiles", methods=["POST"])
def create_profile():
    """Crée un profil utilisateur avec un identifiant unique."""
    profile_id = uuid.uuid4().hex
    PROFILES[profile_id] = {}
    current_app.logger.info("Profil %s créé", profile_id)
    return jsonify({"profile_id": profile_id}), 201

###############################################################################
# 4) Ajout / mise à jour des réponses
###############################################################################
@api_eligibility.route("/profiles/<string:profile_id>/answers", methods=["PUT"])
def update_answers(profile_id: str):
    """Ajoute ou met à jour les réponses d'un profil."""
    if profile_id not in PROFILES:
        return jsonify({"error": "Profil introuvable"}), 404

    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"error": "Format JSON attendu"}), 400

    # Mettre à jour les réponses du profil
    PROFILES[profile_id].update(flatten_keys(payload))
    return jsonify({"saved": True, "answers": PROFILES[profile_id]}), 200

###############################################################################
# 5) Calcul d’éligibilité via profil stocké
###############################################################################
@api_eligibility.route("/profiles/<string:profile_id>/eligibilite", methods=["GET"])
def profil_eligibility(profile_id: str):
    """Calcule l'éligibilité en utilisant les réponses stockées dans un profil."""
    if profile_id not in PROFILES:
        return jsonify({"error": "Profil introuvable"}), 404

    # Calculer l'éligibilité à partir des réponses du profil
    results = calculer_eligibilite(PROFILES[profile_id])
    return jsonify({"profile_id": profile_id, "results": results}), 200

###############################################################################
# Fonction utilitaire pour calculer l'éligibilité
###############################################################################

# Charger les fichiers JSON


def calculer_eligibilite(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule l'éligibilité en fonction des réponses fournies et retourne les procédures éligibles avec leurs documents."""
    moteur = MoteurEligibilite()
    moteur.reset()

    # Déclarer un seul fait Profil avec toutes les réponses
    moteur.declare(Profil(**answers))

    # Exécuter le moteur
    moteur.run()

    # Récupérer les éligibilités
    eligible_ids = [fact["eligibilite"] for fact in moteur.facts.values() if "eligibilite" in fact]
    print(eligible_ids)
    # Construire le résultat avec id, nom et documents requis
    eligible_procedures = []
    for proc_id in eligible_ids:
        if proc_id in proc_doc_map and proc_id in proc_name_map:
            required_docs = [
                {"code": code, "description": doc_map[code]}
                for code in proc_doc_map[proc_id]
                if code in doc_map
            ]
            eligible_procedures.append({
                "id": proc_id,
                "name": proc_name_map[proc_id],
                "required_documents": required_docs
            })

    return eligible_procedures