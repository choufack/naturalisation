import json

class DocumentManager:
    def __init__(self, json_file_path="../schemas/documents_complet.json"):
        self.documents = self._load_documents(json_file_path)
        print(f"Taille : {len(self.documents)}")

    def _load_documents(self, json_file_path):
        # Simulation du chargement depuis un fichier JSON
        # En réalité, cela chargerait documents.json
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            # Données par défaut si le fichier n'est pas trouvé (basées sur votre exemple initial)
            return {
                "Carte de résident - Regroupement familial": {
                    "communs": ["Acte de naissance", "Passeport", "Justificatif de domicile", "Photos", "Taxe"],
                    "conditions": {
                        "housingSituation": {
                            "locataire": ["Bail", "Quittance de loyer"],
                            "proprietaire": ["Taxe d'habitation"]
                        },
                        "family_link": {
                            "mariage": ["Acte de mariage", "Déclaration conjointe"]
                        }
                    }
                },
                "Naturalisation par mariage": {
                    "communs": ["Cerfa 15277*04", "Timbre fiscal 55€", "Photos", "Passeport", "Acte de mariage"],
                    "conditions": {
                        "family_community": {
                            True: ["Bail commun", "Facture EDF"]
                        }
                    }
                }
            }

    def get_documents(self, eligibility, profil):
        if eligibility not in self.documents:
            print(f"Erreur : Éligibilité '{eligibility}' non trouvée dans documents.json")
            return []
        docs = self.documents[eligibility]["communs"].copy()
        for key, conditions in self.documents[eligibility]["conditions"].items():
            value = profil.get(key)
            if value in conditions:
                docs.extend(conditions[value])
        return docs

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialisation du manager
    manager = DocumentManager()

    # Profil de test
    profil = {
        "housingSituation": "locataire",
        "family_link": "mariage",
        "family_community": True
    }

    # Détermination des documents pour une éligibilité
    eligibility = "Carte de résident - Regroupement familial"
    required_docs = manager.get_documents(eligibility, profil)
    print(f"Documents requis pour {eligibility}: {required_docs}")

    eligibility = "Naturalisation par mariage"
    required_docs = manager.get_documents(eligibility, profil)
    print(f"Documents requis pour {eligibility}: {required_docs}")