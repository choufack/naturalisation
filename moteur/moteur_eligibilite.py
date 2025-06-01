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

    @Rule(Profil(family_link='mariage', family_community=True, currentPermit=MATCH.p),
          TEST(lambda p: p not in ['none', 'other']))
    def sejour_vpf_conjoint_francais(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Conjoint de citoyen français'))

    @Rule(Profil(family_link='pacs', family_community=True, currentPermit=MATCH.p),
          TEST(lambda p: p not in ['none', 'other']))
    def sejour_vpf_pacs(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Partenaire Pacsé avec un Français'))

    @Rule(Profil(family_link='parentEnfFr', hasMinorChildren=True, currentPermit=MATCH.p),
          TEST(lambda p: p not in ['none', 'other']))
    def sejour_vpf_parent_enfant_francais(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Parent d\'enfant français mineur'))

    @Rule(Profil(family_link='regroup', ageBracket='<18'))
    def sejour_vpf_reunification_mineur(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Jeune adulte entré par regroupement familial'))

    @Rule(Profil(family_link='famUE', currentPermit=MATCH.p),
          TEST(lambda p: p not in ['none', 'other']))
    def sejour_vpf_eu_long_term_resident(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Membre de famille d\'un étranger résident UE'))

    @Rule(Profil(residenceBracket='born', schoolingFR=True))
    def sejour_vpf_jeune_france(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Jeune né ou entré mineur en France'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'medical' in s))
    def sejour_vpf_pension_accident(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Bénéficiaire pension accident travail'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'volontaire' in s))
    def sejour_vpf_travail_solidaire(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Travail solidaire'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'humanitaire' in s))
    def sejour_vpf_humanitaire(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Raisons humanitaires'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'victimeTraite' in s))
    def sejour_vpf_violence_domestique(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Victime violence domestique'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'victimeTraite' in s))
    def sejour_vpf_traite(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Victime traite ou proxénétisme'))

    # ======================== TRAVAIL ========================
    @Rule(Profil(work_contract='CDI', work_permit=True))
    def sejour_salarie_cdi(self):
        self.declare(Fact(eligibilite='Carte de Séjour "salarié"'))

    @Rule(Profil(work_contract='CDD', work_permit=True))
    def sejour_salarie_cdd(self):
        self.declare(Fact(eligibilite='Carte de Séjour "salarié"'))

    @Rule(Profil(work_contract='detache', work_salary=MATCH.s),
          TEST(lambda s: s >= 1801.8))
    def sejour_ict(self):
        self.declare(Fact(eligibilite='Carte de Séjour "salarié détaché ICT"'))

    @Rule(Profil(work_contract='saisonnier', work_permit=True))
    def sejour_saisonnier(self):
        self.declare(Fact(eligibilite='Carte de Séjour "travailleur saisonnier"'))

    @Rule(Profil(work_contract=MATCH.w, work_permit=True), TEST(lambda w: w in ['CDI', 'CDD', 'saisonnier', 'detache']))
    def sejour_travailleur_temporaire(self):
        self.declare(Fact(eligibilite='Carte de Séjour "travailleur temporaire"'))

    # ======================== ÉTUDES ========================
    @Rule(Profil(studies_status='etudiant', visitor_resources=MATCH.r),
          TEST(lambda r: r in ['1200_1426', 'plus_1426']))
    def sejour_etudiant(self):
        self.declare(Fact(eligibilite='Visa "étudiant" / Carte de Séjour "étudiant"'))

    @Rule(Profil(studies_status='stagiaire'))
    def sejour_stagiaire(self):
        self.declare(Fact(eligibilite='Visa ou Carte de Séjour "stagiaire"'))

    @Rule(Profil(studies_status='chercheur'))
    def sejour_chercheur(self):
        self.declare(Fact(eligibilite='Passeport talent – chercheur'))

    @Rule(Profil(studies_status='etudiant', visitor_resources=MATCH.r),
          TEST(lambda r: r in ['1200_1426', 'plus_1426']))
    def sejour_mobilite_etudiant(self):
        self.declare(Fact(eligibilite='Carte de Séjour "étudiant - programme de mobilité"'))

    # ======================== INVEST / TALENT ========================
    @Rule(Profil(invest_registered=True, invest_hasBP=True, invest_funds=MATCH.f),
          TEST(lambda f: f > 0))
    def sejour_entrepreneur(self):
        self.declare(Fact(eligibilite='Carte de Séjour "entrepreneur/profession libérale"'))

    @Rule(Profil(studies_degree=MATCH.d, work_contract=MATCH.c, work_salary=MATCH.s),
          TEST(lambda d, c, s: d != '' and c in ['CDI', 'CDD'] and s >= 43243))
    def passeport_talent_salarie(self):
        self.declare(Fact(eligibilite='Passeport talent – salarié qualifié'))

    @Rule(Profil(work_contract=MATCH.c, work_salary=MATCH.s),
          TEST(lambda c,s : c in ['CDI', 'CDD'] and s >= 43243))
    def passeport_talent_recrute(self):
        self.declare(Fact(eligibilite='Passeport talent – recrutement entreprise innovante'))

    @Rule(Profil(studies_degree=MATCH.d, work_contract=MATCH.c, work_salary=MATCH.s),
          TEST(lambda d,c,s: d != ''and c in ['CDI', 'CDD'] and s >= 53836.5))
    def passeport_talent_carte_bleue(self):
        self.declare(Fact(eligibilite='Passeport talent – carte bleue européenne'))

    @Rule(Profil(work_contract='detache', work_salary=MATCH.s),
          TEST(lambda s: s >= 38918.88))
    def passeport_talent_mission(self):
        self.declare(Fact(eligibilite='Passeport talent – salarié en mission'))

    @Rule(Profil(studies_degree=MATCH.d, invest_hasBP=True),
          TEST(lambda d: d != ''))
    def passeport_talent_creation(self):
        self.declare(Fact(eligibilite='Passeport talent – création d’entreprise'))

    @Rule(Profil(invest_hasBP=True))
    def passeport_talent_projet(self):
        self.declare(Fact(eligibilite='Passeport talent – projet innovant'))

    @Rule(Profil(invest_funds=MATCH.f),
          TEST(lambda f: f >= 10000))
    def passeport_talent_investisseur(self):
        self.declare(Fact(eligibilite='Passeport talent – investisseur'))

    @Rule(Profil(work_contract=MATCH.c, work_salary=MATCH.s),
          TEST(lambda c,s: c in ['CDI', 'CDD'] and s >= 64864.8))
    def passeport_talent_mandataire(self):
        self.declare(Fact(eligibilite='Passeport talent – mandataire social'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'talentArtiste' in s))
    def passeport_talent_artiste(self):
        self.declare(Fact(eligibilite='Passeport talent – profession artistique et culturelle'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'talentArtiste' in s))
    def passeport_talent_renomme(self):
        self.declare(Fact(eligibilite='Passeport talent – personne de renommée internationale'))

    @Rule(Profil(family_link=MATCH.f), TEST(lambda f: f in ['mariage', 'parentEnfFr']))
    def passeport_talent_famille(self):
        self.declare(Fact(eligibilite='Passeport talent (famille)'))

    # ======================== VISITEUR ========================
    @Rule(Profil(visitor_resources='plus_1426', visitor_housing=MATCH.h),
          TEST(lambda h: h in ['locataire', 'proprietaire', 'heberge']))
    def sejour_visiteur(self):
        self.declare(Fact(eligibilite='Carte de Séjour "visiteur"'))

    # ======================== SITUATIONS SPÉCIALES ========================
    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'auPair' in s))
    def sejour_au_pair(self):
        self.declare(Fact(eligibilite='Carte de Séjour "jeune au pair"'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'volontaire' in s))
    def aps_volontariat(self):
        self.declare(Fact(eligibilite='APS – mission de volontariat'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'parentSickChild' in s))
    def aps_parent_malade(self):
        self.declare(Fact(eligibilite='APS – parent d’enfant malade'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'victimeTraite' in s))
    def sejour_protection(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Victime traite ou proxénétisme'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'humanitaire' in s))
    def sejour_humanitaire(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Raisons humanitaires'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'medical' in s))
    def sejour_medical(self):
        self.declare(Fact(eligibilite='Carte de séjour pour soins médicaux en France'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'ancienCombattant' in s))
    def carte_ancien_combattant(self):
        self.declare(Fact(eligibilite='Carte de séjour « ancien combattant / FFI »'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'refugie' in s))
    def titre_refugie(self):
        self.declare(Fact(eligibilite='Titre de séjour réfugié / protection subsidiaire'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'talentArtiste' in s))
    def passeport_talent_artiste_special(self):
        self.declare(Fact(eligibilite='Passeport talent – artiste / interprète'))

    @Rule(Profil(specialSituations=MATCH.s), TEST(lambda s: 'sportifPro' in s))
    def passeport_talent_sportif(self):
        self.declare(Fact(eligibilite='Passeport talent – sportif professionnel'))

    # ======================== RÉSIDENCE LONGUE DURÉE ========================
    @Rule(Profil(yearsResidence=MATCH.y, resident_languageA2=True, stableIncome=True),
          TEST(lambda y: y >= 5))
    def carte_resident_ld_ue(self):
        self.declare(Fact(eligibilite='Carte de Résident Longue Durée - UE'))

    @Rule(Profil(family_link='mariage', family_yearsMarriage=MATCH.y, family_community=True, resident_languageA2=True),
          TEST(lambda y: y >= 3))
    def carte_resident_epoux(self):
        self.declare(Fact(eligibilite='Carte de Résident - Époux de Français'))

    # ======================== NATURALISATION ========================
    @Rule(Profil(mainPath='ascendant', ascendant_link=MATCH.a, residenceBracket='>10'),
          TEST(lambda a: a in ['parent', 'grandparent']))
    def naturalisation_ascendant(self):
        self.declare(Fact(eligibilite='Naturalisation par Déclaration – Ascendant'))

    @Rule(Profil(mainPath='sibling', schoolingFR=True))
    def naturalisation_fratrie(self):
        self.declare(Fact(eligibilite='Naturalisation par Déclaration – Fratrie'))

    @Rule(Profil(mainPath='mariage', marriage4y=True, communityLife=True, frenchB1=True))
    def naturalisation_mariage(self):
        self.declare(Fact(eligibilite='Naturalisation par Déclaration – Mariage'))

    @Rule(Profil(yearsResidence=MATCH.y, pluri_integrationOK=True, frenchB1=True),
          TEST(lambda y: y >= 5))
    def naturalisation_decret(self):
        self.declare(Fact(eligibilite='Naturalisation par Décret'))

    # ======================== AUTRES ========================
    @Rule(Profil(nationality_sim=MATCH.n, work_contract=MATCH.c),
          TEST(lambda n,c: n in ['FR', 'GB'] and c in ['CDI', 'CDD']))
    def sejour_eu_travailleur(self):
        self.declare(Fact(eligibilite='Carte de Séjour pour Européen - Travailleur'))

    @Rule(Profil(nationality_sim=MATCH.n, studies_status='etudiant'),
          TEST(lambda n: n in ['FR', 'GB']))
    def sejour_eu_etudiant(self):
        self.declare(Fact(eligibilite='Carte de Séjour pour Européen - Étudiant'))

    @Rule(Profil(nationality_sim=MATCH.n, specialSituations=MATCH.s),
          TEST(lambda n,s: n in ['FR', 'GB'] and 'retraite' in s))
    def sejour_eu_retraite(self):
        self.declare(Fact(eligibilite='Carte de Séjour pour Européen - Retraité ou inactif'))

    @Rule(Profil(family_link='famUE'))
    def sejour_eu_famille(self):
        self.declare(Fact(eligibilite='Carte de Séjour pour Européen - Membre de la famille'))

    @Rule(Profil(ageBracket='<18', hasMinorChildren=True))
    def document_mineur(self):
        self.declare(Fact(eligibilite='Document de Circulation pour Mineur Étranger'))

    # ======================== DURÉE DE RÉSIDENCE ========================
    @Rule(Profil(yearsResidence=MATCH.y),
          TEST(lambda y: y >= 10))
    def sejour_longue_residence(self):
        self.declare(Fact(eligibilite='Carte de séjour pour résidence habituelle de plus de 10 ans'))

    # ======================== CERTIFICATS ALGÉRIENS ========================
    @Rule(Profil(nationality_sim='DZ', alg1_motif=MATCH.m),
          TEST(lambda m: m in ['mariage', 'parent', 'etat_sante', 'vie_priv']))
    def certificat_alg_1an(self):
        self.declare(Fact(eligibilite='Certificat algérien 1 an'))

    @Rule(Profil(nationality_sim='DZ', alg10_type=MATCH.t),
          TEST(lambda t: t in ['res10', 'famViePriv', 'francophone', 'rente']))
    def certificat_alg_10ans(self):
        self.declare(Fact(eligibilite='Certificat algérien 10 ans'))

    # ======================== PLURIANNUELLE ========================
    @Rule(Profil(currentPermit=MATCH.c, pluri_integrationOK=True),
          TEST(lambda c: c.startswith('csp_')))
    def carte_pluriannuelle(self):
        self.declare(Fact(eligibilite='Carte de Séjour Pluriannuelle "générale"'))




###############################################################################
# 3.  UTILITAIRE : aplatissement des clés et conversion des valeurs
###############################################################################


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
