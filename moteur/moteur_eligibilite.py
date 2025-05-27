# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, request
from experta import *

app = Flask(__name__)

###############################################################################
# 1. PROFIL : toutes les clés issues du questionnaire
###############################################################################
class Profil(Fact):
    """Fact porteur de toutes les réponses du formulaire.
    Les clés avec un point (ex. family.link) seront aplaties en
    family_link via flatten_keys()."""
    pass

###############################################################################
# 2. MOTEUR D'ÉLIGIBILITÉ
###############################################################################
class MoteurEligibilite(KnowledgeEngine):

    # ======================== FAMILLE ========================
    @Rule(
        Profil(family_link='mariage', family_community=True, family_yearsMarriage=MATCH.y),
        TEST(lambda y: y >= 4)
    )
    def nationalite_par_mariage(self):
        self.declare(Fact(eligibilite='Nationalité française par mariage (≥ 4 ans)'))

    # @Rule(Profil(family_link="mariage", family_community=True, family_yearsMarriage=MATCH.y), TEST(lambda y: y >= 4))
    # def nationalite_par_mariage(self):
    #     print("Règle activée : Nationalité par mariage")
    #     self.declare(Fact(eligibilite="Nationalité française par mariage (≥ 4 ans)"))

    @Rule(Profil(family_link='pacs', family_community=True))
    def sejour_pacs(self):
        self.declare(Fact(eligibilite='Carte VP&F – partenaire Pacsé avec un Français'))

    @Rule(Profil(family_link='parentEnfFr'))
    def sejour_parent_enfant_francais(self):
        self.declare(Fact(eligibilite='Carte VP&F – parent d’enfant français'))

    @Rule(Profil(family_link='regroupement'))
    def sejour_regroupement_familial(self):
        self.declare(Fact(eligibilite='Carte de séjour – regroupement familial'))

    @Rule(Profil(family_link='famUE'))
    def sejour_famille_ue(self):
        self.declare(Fact(eligibilite='Carte de séjour – membre de famille citoyen UE/EEE'))

    # ======================== TRAVAIL ========================
    @Rule(Profil(work_contract='CDI', work_permit=True))
    def sejour_salarie_cdi(self):
        self.declare(Fact(eligibilite='Carte de séjour « salarié »'))
    
    @Rule(Profil(work_contract='CDD', work_permit=True))
    def sejour_salarie_cdd(self):
        self.declare(Fact(eligibilite='Carte de séjour « salarié »'))
        
    # @Rule(Profil(work_contract=MATCH.c, work_permit=True), TEST(lambda c: c in ('CDI', 'CDD')))
    # def sejour_salarie(self):
    #     self.declare(Fact(eligibilite='Carte de séjour « salarié »'))

    @Rule(Profil(work_contract='detache'))
    def sejour_ict(self):
        self.declare(Fact(eligibilite='Carte de séjour « salarié détaché ICT »'))

    @Rule(Profil(work_contract='saisonnier'))
    def sejour_saisonnier(self):
        self.declare(Fact(eligibilite='Carte de séjour « travailleur saisonnier »'))

    # ======================== ÉTUDES ========================
    @Rule(Profil(studies_status='etudiant'))
    def sejour_etudiant(self):
        self.declare(Fact(eligibilite='Carte de séjour « étudiant »'))

    @Rule(Profil(studies_status='stagiaire'))
    def sejour_stagiaire(self):
        self.declare(Fact(eligibilite='Carte de séjour « stagiaire »'))

    @Rule(Profil(studies_status='chercheur'))
    def sejour_chercheur(self):
        self.declare(Fact(eligibilite='Passeport talent – chercheur'))

    # ======================== INVEST / TALENT ========================
    @Rule(
        Profil(invest_registered=True, invest_hasBP=True),
        AS.profil << Profil(invest_funds=MATCH.f),
        TEST(lambda f: int(f) >= 30000 if f is not None else False)
    )
    def passeport_talent_entrepreneur(self):
        self.declare(Fact(eligibilite='Passeport talent – création d’entreprise (≥ 30 000 €)'))

    @Rule(Profil(invest_registered=True))
    def sejour_entrepreneur(self):
        self.declare(Fact(eligibilite='Carte de séjour « entrepreneur / profession libérale »'))

    # ======================== VISITEUR ========================
    @Rule(Profil(visitor_resources=MATCH.r), TEST(lambda r: r in ('1200_1426', 'plus_1426')))
    def sejour_visiteur(self):
        self.declare(Fact(eligibilite='Carte de séjour « visiteur » (ressources suffisantes)'))

    # ======================== SITUATIONS SPÉCIALES ========================
    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'auPair' in s))
    def sejour_au_pair(self):
        self.declare(Fact(eligibilite='Carte de séjour « jeune au pair »'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'volontaire' in s))
    def sejour_volontaire(self):
        self.declare(Fact(eligibilite='Autorisation de séjour – volontariat'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'medical' in s))
    def sejour_medical(self):
        self.declare(Fact(eligibilite='Carte de séjour pour soins médicaux en France'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'victimeTraite' in s))
    def sejour_protection(self):
        self.declare(Fact(eligibilite='Carte – protection des victimes de traite ou proxénétisme'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'parentSickChild' in s))
    def sejour_parent_enfant_malade(self):
        self.declare(Fact(eligibilite='APS – parent d’enfant malade'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'ancienCombattant' in s))
    def carte_ancien_combattant(self):
        self.declare(Fact(eligibilite='Carte de séjour « ancien combattant / FFI »'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'refugie' in s))
    def titre_refugie(self):
        self.declare(Fact(eligibilite='Titre de séjour réfugié / protection subsidiaire'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'humanitaire' in s))
    def sejour_humanitaire(self):
        self.declare(Fact(eligibilite='Carte de séjour pour motif humanitaire'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'talentArtiste' in s))
    def passeport_talent_artiste(self):
        self.declare(Fact(eligibilite='Passeport talent – artiste / interprète'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'sportifPro' in s))
    def passeport_talent_sportif(self):
        self.declare(Fact(eligibilite='Passeport talent – sportif professionnel'))

    # ======================== DURÉE DE RÉSIDENCE ========================
    @Rule(Profil(yearsResidence=MATCH.y), TEST(lambda y: y >= 10))
    def sejour_longue_residence(self):
        self.declare(Fact(eligibilite='Carte de séjour pour résidence habituelle de plus de 10 ans'))

    # ------------------------------------------------------------------
    #  Ajoutez ici d'autres règles si nécessaire (certificats algériens,
    #  carte de résident longue durée UE, etc.)
    # ------------------------------------------------------------------

###############################################################################
# 3.  UTILITAIRE : aplatissement des clés et conversion des valeurs
###############################################################################

# def flatten_keys(form):
#     """Convertit les clés dot‑notation en snake_case et adapte les types."""
#     out = {}
#     for k in form:
#         key = k.replace('.', '_')
#         # Handle both Flask request.form and regular dict
#         values = form.getlist(k) if hasattr(form, 'getlist') else [form[k]]

#         # Checkbox = liste
#         if len(values) > 1:
#             out[key] = values
#             continue

#         v = values[0]
#         # Tentative de conversion en entier d'abord
#         try:
#             out[key] = int(v)
#         except (ValueError, TypeError):
#             # Si ce n'est pas un entier, traiter comme une chaîne
#             if isinstance(v, str) and v.lower() in ('oui', 'non', 'true', 'false'):
#                 out[key] = v.lower() in ('oui', 'true')
#             else:
#                 out[key] = v
#     return out


def flatten_keys(form):
    """Convertit les clés dot-notation en snake_case et adapte les types.
    Version améliorée avec meilleure gestion des erreurs."""
    out = {}
    for k in form:
        key = k.replace('.', '_')
        values = form.getlist(k) if hasattr(form, 'getlist') else [form[k]]
        
        # Checkbox/multi-select = liste
        if len(values) > 1:
            out[key] = values
            continue

        v = values[0]
        
        # Gérer les entrées vides
        if v == '' or v is None:
            out[key] = None
            continue
        
        # Tentative de conversion en entier
        try:
            out[key] = int(v)
        except (ValueError, TypeError):
            # Gestion des booléens
            if isinstance(v, str):
                v_lower = v.lower()
                if v_lower in ('oui', 'true'):
                    out[key] = True
                elif v_lower in ('non', 'false'):
                    out[key] = False
                else:
                    out[key] = v
            else:
                out[key] = v
    
    return out
###############################################################################
# 4.  ROUTE PRINCIPALE (démo Jinja)
###############################################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    resultats = []
    if request.method == 'POST':
        data = flatten_keys(request.form)
        moteur = MoteurEligibilite()
        moteur.reset()
        moteur.declare(Profil(**data))
        moteur.run()
        resultats = [
            f['eligibilite']
            for f in moteur.facts.values()
            if isinstance(f, Fact) and f.get('eligibilite')
        ]

    return render_template_string('''
    <h1>Test d\'éligibilité titre / nationalité</h1>
    <form method="post">
        <!-- PLACEHOLDER : votre formulaire dynamique (React / Jinja) -->
        <button type="submit">Tester</button>
    </form>
    {% if resultats %}
        <h2>Résultats :</h2>
        <ul>{% for r in resultats %}<li>{{ r }}</li>{% endfor %}</ul>
    {% endif %}
    ''', resultats=resultats)


if __name__ == '__main__':
    app.run(debug=True)
