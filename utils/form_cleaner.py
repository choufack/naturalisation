import json
from typing import Dict, Any, List
from copy import deepcopy

# Charger les fichiers JSON
with open('./schemas/new/parcours_titre_sejour.json', 'r', encoding='utf-8') as f:
    titre_sejour_data = json.load(f)

with open('./schemas/new/nationality_questions.json', 'r', encoding='utf-8') as f:
    nationality_data = json.load(f)

def evaluate_condition(condition: Dict[str, Any], answers: Dict[str, Any]) -> bool:
    """Évalue une condition visible_if en fonction des réponses."""
    fact = condition['fact'].replace('.', '_')  # Convertir . en _ pour correspondre à answers
    value = answers.get(fact)
    
    operator = condition.get('eq') and 'eq' or \
              condition.get('in') and 'in' or \
              condition.get('contains') and 'contains' or \
              condition.get('nin') and 'nin' or \
              condition.get('starts_with') and 'starts_with' or \
              condition.get('not_contains') and 'not_contains'
    
    condition_value = condition[operator]
    
    if value is None:
        return False
    
    if operator == 'eq':
        return value == condition_value
    elif operator == 'in':
        return value in condition_value
    elif operator == 'contains':
        if isinstance(value, list):
            return condition_value in value
        return False
    elif operator == 'nin':
        return value not in condition_value
    elif operator == 'starts_with':
        return isinstance(value, str) and value.startswith(condition_value)
    elif operator == 'not_contains':
        if isinstance(value, list):
            return condition_value not in value
        return True
    return False

def is_visible(conditions: List[Dict[str, Any]], answers: Dict[str, Any]) -> bool:
    """Vérifie si toutes les conditions visible_if sont satisfaites."""
    if not conditions:
        return True
    return all(evaluate_condition(cond, answers) for cond in conditions)

def clean_form_data(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Nettoie les données du formulaire en supprimant les réponses invisibles."""
    # Faire une copie pour éviter de modifier l'original
    cleaned_answers = deepcopy(answers)
    
    # Convertir les clés de _ en . pour correspondre aux facts
    normalized_answers = {}
    for key, value in cleaned_answers.items():
        normalized_key = key.replace('_', '.')
        normalized_answers[normalized_key] = value
    
    # Liste des facts à vérifier (pivots + panels des deux fichiers)
    all_questions = []
    
    # Ajouter les pivots (questions globales)
    for data in [titre_sejour_data, nationality_data]:
        for pivot in data.get('pivots', []):
            all_questions.append({
                'fact': pivot['fact'],
                'visible_if': [],
                'is_panel': False
            })
    
    # Ajouter les questions des panneaux
    for data in [titre_sejour_data, nationality_data]:
        for panel in data.get('panels', []):
            for question in panel.get('questions', []):
                all_questions.append({
                    'fact': question['fact'],
                    'visible_if': panel['visible_if'] + question.get('visible_if', []),
                    'is_panel': False
                })
    
    # Vérifier chaque fact
    for question in all_questions:
        fact = question['fact']
        if not is_visible(question['visible_if'], normalized_answers):
            # Supprimer le fact s'il n'est pas visible
            fact_with_underscore = fact.replace('.', '_')
            if fact_with_underscore in cleaned_answers:
                del cleaned_answers[fact_with_underscore]
    
    return cleaned_answers

# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple de données avec des réponses non pertinentes
    test_answers = {
        "nationality": "DZ",
        "currentPermit": "vls_vpf",
        "yearsResidence": "1-3",
        "motifPrincipal": ["travail"],  # Pas de famille, donc family.* devrait être supprimé
        "housingSituation": "locataire",
        "specialSituations": ["aucune"],
        "family_link": "mariage",  # Ne devrait pas être visible
        "family_yearsMarriage": 5,  # Ne devrait pas être visible
        "work_contract": "CDI",
        "work_permit": True
    }
    
    cleaned = clean_form_data(test_answers)
    print(json.dumps(cleaned, ensure_ascii=False, indent=2))