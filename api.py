import json
import uuid
from typing import Dict, Any
from flask import Blueprint, jsonify, request, current_app
from moteur.moteur_eligibilite import MoteurEligibilite, Profil, flatten_keys
# from utils.helpers import flatten_keys  # Assurez-vous que cette fonction est définie
# from utils.constants import JSON_PATH  # Chemin vers le fichier questions.json

# Chemin relatif vers le fichier questions.json
NAT_JSON_PATH = "schemas/question_nat.json"
TITLE_JSON_PATH = "schemas/question_titre.json"

# Création du Blueprint pour l'API
api_eligibility = Blueprint("api", __name__)

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
    print(answers)  # Debugging output
    results = calculer_eligibilite(answers)
    print(f"results: {results}")  # Debugging output
    return jsonify({"results": results}), 200

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
def calculer_eligibilite(answers: Dict[str, Any]) -> list:
    """Calcule l'éligibilité en fonction des réponses fournies."""
    moteur = MoteurEligibilite()
    moteur.reset()

    
    # Déclarer un seul fait Profil avec toutes les réponses
    moteur.declare(Profil(**answers))

    # Exécuter le moteur
    moteur.run()

    # Récupérer les résultats
    return [fact["eligibilite"] for fact in moteur.facts.values() if "eligibilite" in fact]