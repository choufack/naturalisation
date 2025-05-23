from flask import Flask, request, jsonify
from moteur.moteur_eligibilite import MoteurEligibilite, Profil
from experta import Fact

app = Flask(__name__)

@app.route('/eligibilite', methods=['POST'])
def calculer_eligibilite():
    """
    Endpoint pour calculer l'éligibilité.
    Reçoit les données utilisateur en JSON et retourne les résultats.
    """
    try:
        # Récupérer les données JSON envoyées par le client
        data = request.json
        if not data:
            return jsonify({"error": "Aucune donnée reçue"}), 400

        # Initialiser le moteur d'éligibilité
        moteur = MoteurEligibilite()
        moteur.reset()

        # Déclarer les faits basés sur les données reçues
        for key, value in data.items():
            moteur.declare(Profil(**{key: value}))

        # Exécuter le moteur
        moteur.run()

        # Récupérer les résultats
        results = [fact['eligibilite'] for fact in moteur.facts.values() if 'eligibilite' in fact]

        # Retourner les résultats sous forme de JSON
        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)