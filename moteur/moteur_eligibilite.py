# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, request
from experta import *
from .documentManager import DocumentManager
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

    # ======================== NATIONALITÉ ========================
    @Rule(
        Profil(mainPath='ascendant', ascendant_link=MATCH.l),
        TEST(lambda l: l in ['parent', 'grandparent']),
        Profil(residenceBracket=MATCH.r),
        TEST(lambda r: r in ['born', '>10'])
    )
    def nationalite_ascendant(self):
        self.declare(Fact(eligibilite='P045'))

    @Rule(
        Profil(mainPath='sibling', schoolingFR=True),
        Profil(residenceBracket=MATCH.r),
        TEST(lambda r: r in ['born', '>10'])
    )
    def nationalite_frere_soeur(self):
        self.declare(Fact(eligibilite='P046'))

    @Rule(
        Profil(mainPath='mariage', marriage4y=True, communityLife=True, frenchB1=MATCH.lb),
        TEST(lambda lb: lb not in ['aucun','pas_de_preuve'])
    )
    def nationalite_par_mariage(self):
        self.declare(Fact(eligibilite='P047'))
        
    @Rule(
        Profil(mainPath='mariage', marriage4y=True, communityLife=True, frenchB1=MATCH.lb),
        TEST(lambda lb: lb in ['aucun','pas_de_preuve'])
    )
    def nationalite_par_mariage2(self):
        self.declare(Fact(eligibilite='P0470'))

    @Rule(
        Profil(mainPath='adoption', adoptionPleniere=True)
    )
    def nationalite_enfant_adopte(self):
        self.declare(Fact(eligibilite='P048'))

    @Rule(
        Profil(mainPath='adoption', recueil3ans=True)
    )
    def nationalite_enfant_recueilli(self):
        self.declare(Fact(eligibilite='P049'))

    @Rule(
        Profil(mainPath='reintegration', strongLinks=True)
    )
    def reintegration_declaration(self):
        self.declare(Fact(eligibilite='P050'))

    @Rule(
        Profil(mainPath='reintegration'),
        Profil(residenceBracket=MATCH.r),
        TEST(lambda r: r in ['5-10', '>10', 'born']),
        Profil(cleanRecord=True ,frenchB1=MATCH.lb),
        TEST(lambda lb: lb not in ['aucun','pas_de_preuve'])
    )
    def reintegration_decret(self):
        self.declare(Fact(eligibilite='P051'))
        
    @Rule(
        Profil(mainPath='reintegration'),
        Profil(residenceBracket=MATCH.r),
        TEST(lambda r: r in ['5-10', '>10', 'born']),
        Profil(cleanRecord=True ,frenchB1=MATCH.lb),
        TEST(lambda lb: lb  in ['aucun','pas_de_preuve'])
    )
    def reintegration_decret2(self):
        self.declare(Fact(eligibilite='P0510'))

    @Rule(
        Profil(mainPath='naturalisation'),
        Profil(residenceBracket=MATCH.r),
        TEST(lambda r: r in ['5-10', '>10', 'born']),
        Profil(stableIncome5y=True, cleanRecord=True, longAbsence=False,frenchB1=MATCH.lb),
        TEST(lambda lb: lb not in ['aucun','pas_de_preuve'])
    )
    def naturalisation_decret(self):
        self.declare(Fact(eligibilite='P052'))
        
    @Rule(
        Profil(mainPath='naturalisation'),
        Profil(residenceBracket=MATCH.r),
        TEST(lambda r: r in ['5-10', '>10', 'born']),
        Profil(stableIncome5y=True, cleanRecord=True, longAbsence=False,frenchB1=MATCH.lb),
        TEST(lambda lb: lb in ['aucun','pas_de_preuve'])
    )
    def naturalisation_decret2(self):
        self.declare(Fact(eligibilite='P0520'))

    @Rule(
        Profil(mainPath='jus_soli', res5since11=True, ageBracket='>=18', residenceBracket='born')
    )
    def nationalite_enfant_ne_france(self):
        self.declare(Fact(eligibilite='P053'))

    @Rule(
        Profil(specialSituations=MATCH.s),
        TEST(lambda s: 'refugie' in s),
        Profil(yearsResidence=MATCH.y),
        TEST(lambda y: y in ['3-5', '>5']),
        Profil(frenchB1=MATCH.lb),
        TEST(lambda lb: lb not in ['aucun','pas_de_preuve'])
    )
    def naturalisation_refugie(self):
        self.declare(Fact(eligibilite='P055'))
        
    @Rule(
        Profil(specialSituations=MATCH.s),
        TEST(lambda s: 'refugie' in s),
        Profil(yearsResidence=MATCH.y),
        TEST(lambda y: y in ['3-5', '>5']),
        Profil(frenchB1=MATCH.lb),
        TEST(lambda lb: lb  in ['aucun','pas_de_preuve'])
    )
    def naturalisation_refugie2(self):
        self.declare(Fact(eligibilite='P0550'))
        
    @Rule(
        Profil(nationality=MATCH.n),
        TEST(lambda n: n == 'STATELESS'),
        Profil(yearsResidence=MATCH.y),
        TEST(lambda y: y != '<3'),
        # TODO: ajouter condition sur le niveau de langue (prise en compte du message pour lui de faire les cours de langue si qucun justificatif)
    )
    def naturalisation_refugie3(self):
        self.declare(Fact(eligibilite='P055'))

    # ======================== FAMILLE ========================
    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'famille' in m),
        Profil(family_link='mariage', family_yearsMarriage=MATCH.y, family_community=True),
        TEST(lambda y: y >= 1)
    )
    def sejour_conjoint_francais(self):
        self.declare(Fact(eligibilite='P001'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'famille' in m),
        Profil(family_link='pacs', family_yearsMarriage=MATCH.y, family_community=True),
        TEST(lambda y: y >= 1)
    )
    def sejour_pacs(self):
        self.declare(Fact(eligibilite='P002'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'famille' in m),
        Profil(family_link='parentEnfFr', hasMinorChildren=True)
    )
    def sejour_parent_enfant_francais(self):
        self.declare(Fact(eligibilite='P003'))

    @Rule(
        Profil(mainPath='jus_soli', res5since11=True),
        Profil(ageBracket=MATCH.a),
        TEST(lambda a: a in ['<18', '>=18']),
        Profil(nationality=MATCH.n),
        TEST(lambda n: n != 'FR')
    )
    def sejour_jeune_mineur(self):
        self.declare(Fact(eligibilite='P006'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'famille' in m),
        Profil(family_link='famUE', family_community=True, currentPermit='resident_10ans')
    )
    def sejour_famille_resident_ue(self):
        self.declare(Fact(eligibilite='P004'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'famille' in m),
        Profil(family_link='regroup', ageBracket='>=18')
    )
    def sejour_jeune_regroupement(self):
        self.declare(Fact(eligibilite='P005'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'autre' in m),
        Profil(yearsResidence=MATCH.y),
        TEST(lambda y: y in ['3-5', '>5'])
    )
    def sejour_humanitaire(self):
        self.declare(Fact(eligibilite='P009'))

    @Rule(
        Profil(specialSituations=MATCH.s),
        TEST(lambda s: 'victimeTraite' in s),
        Profil(cleanRecord=True)
    )
    def sejour_victime_traite(self):
        self.declare(Fact(eligibilite='P011'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'famille' in m),
        Profil(family_link='mariage', family_yearsMarriage=MATCH.y, family_community=True, resident_integrationOK=True, resident_languageA2=MATCH.l),
        TEST(lambda y, l: y >= 3 and l not in ['pas_de_preuve','aucun'])
    )
    def resident_epoux_francais(self):
        self.declare(Fact(eligibilite='P031'))
        
    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'famille' in m),
        Profil(family_link='mariage', family_yearsMarriage=MATCH.y, family_community=True, resident_integrationOK=True, resident_languageA2=MATCH.l),
        TEST(lambda y, l: y >= 3 and l in ['pas_de_preuve','aucun'])
    )
    def resident_epoux_francais2(self):
        self.declare(Fact(eligibilite='P0310'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'famille' in m),
        Profil(family_link='regroup', family_community=True),
        Profil(yearsResidence=MATCH.y),
        TEST(lambda y: y in ['3-5', '>5'])
    )
    def resident_regroupement(self):
        self.declare(Fact(eligibilite='P033'))

    @Rule(
        Profil(nationality='DZ'),
        Profil(family_link='regroup', family_community=True)
    )
    def certificat_algerien_regroupement(self):
        self.declare(Fact(eligibilite='P034'))

    @Rule(
        Profil(mainPath='ascendant'),
        Profil(ascendant_link=MATCH.al),
        TEST(lambda al: al in ['parent', 'grandparent']),
        Profil(resident_integrationOK=True, resident_languageA2=MATCH.lb),
        TEST(lambda lb: lb not in  ['pas_de_preuve',"aucun"])
    )
    def resident_ascendant_enfant_francais(self):
        self.declare(Fact(eligibilite='P037'))
        
    @Rule(
        Profil(mainPath='ascendant'),
        Profil(ascendant_link=MATCH.al),
        TEST(lambda al: al in ['parent', 'grandparent']),
        Profil(resident_integrationOK=True, resident_languageA2=MATCH.lb),
        TEST(lambda lb: lb  in ['pas_de_preuve',"aucun"])
    )
    def resident_ascendant_enfant_francais2(self):
        self.declare(Fact(eligibilite='P0370'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'famille' in m),
        Profil(family_link='mariage')
    )
    def passeport_talent_famille(self):
        self.declare(Fact(eligibilite='P027'))

    # ======================== TRAVAIL ========================
    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'travail' in m),
        Profil(work_contract='CDI', work_permit=True, cleanRecord=True)
    )
    def sejour_salarie(self):
        self.declare(Fact(eligibilite='P012'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'travail' in m),
        Profil(work_contract='CDD', work_permit=True, cleanRecord=True)
    )
    def sejour_travailleur_temporaire(self):
        self.declare(Fact(eligibilite='P013'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'travail' in m),
        Profil(work_contract='detache', work_salary=MATCH.s),
        TEST(lambda s: s in ["1600-2500", "2500-3500", "3500-5000", ">5000"])
    )
    def sejour_salarie_detache_ict(self):
        self.declare(Fact(eligibilite='P041'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'travail' in m),
        Profil(work_contract='saisonnier', work_permit=True)
    )
    def sejour_travailleur_saisonnier(self):
        self.declare(Fact(eligibilite='P028'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'travail' in m),
        Profil(studies_degree=MATCH.d),
        TEST(lambda d: d in ['master', 'doctorat']),
        Profil(work_salary=MATCH.s),
        TEST(lambda s: s in ["3500-5000", ">5000"])
    )
    def passeport_talent_salarie_qualifie(self):
        self.declare(Fact(eligibilite='P016'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'travail' in m),
        Profil(work_salary=MATCH.s),
        TEST(lambda s: s in ["3500-5000", ">5000"])
    )
    def passeport_talent_entreprise_innovante(self):
        self.declare(Fact(eligibilite='P017'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'travail' in m),
        Profil(studies_degree=MATCH.d),
        TEST(lambda d: d in ['licence', 'master', 'doctorat']),
        Profil(work_salary=MATCH.s),
        TEST(lambda s: s in ["3500-5000", ">5000"])
    )
    def passeport_talent_carte_bleue(self):
        self.declare(Fact(eligibilite='P018'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'travail' in m),
        Profil(work_contract='detache', work_salary=MATCH.s),
        TEST(lambda s: s in ["3500-5000", ">5000"])
    )
    def passeport_talent_salarie_mission(self):
        self.declare(Fact(eligibilite='P019'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'travail' in m),
        Profil(work_salary=MATCH.s),
        TEST(lambda s: s in [">5000"])
    )
    def passeport_talent_mandataire_social(self):
        self.declare(Fact(eligibilite='P024'))

    # ======================== ÉTUDES ========================
    @Rule(
        Profil(nationality='DZ'),
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'etudes' in m),
        Profil(studies_status='etudiant')
    )
    def certificat_algerien_etudiant(self):
        self.declare(Fact(eligibilite='P043'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'etudes' in m),
        Profil(studies_status='chercheur'),
        Profil(studies_degree=MATCH.d),
        TEST(lambda d: d in ['master', 'doctorat'])
    )
    def passeport_talent_chercheur(self):
        self.declare(Fact(eligibilite='P020'))

    @Rule(
        Profil(currentPermit=MATCH.p),
        TEST(lambda p: p in ['vls_etudiant', 'cs_etudiant']),
        Profil(studies_degree=MATCH.d),
        TEST(lambda d: d in ['master', 'doctorat'])
    )
    def sejour_recherche_emploi_etudiant(self):
        self.declare(Fact(eligibilite='P038'))

    @Rule(
        Profil(currentPermit='vls_chercheur', studies_status='chercheur')
    )
    def sejour_recherche_emploi_chercheur(self):
        self.declare(Fact(eligibilite='P039'))

    @Rule(
        Profil(bilateralAgreement=True),
        Profil(currentPermit=MATCH.p),
        TEST(lambda p: p in ['vls_etudiant', 'cs_etudiant'])
    )
    def aps_recherche_emploi_bilateral(self):
        self.declare(Fact(eligibilite='P040'))

    # ======================== INVESTISSEMENT ========================
    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'invest' in m),
        Profil(invest_registered=True, invest_hasBP=True, invest_funds=MATCH.f),
        TEST(lambda f: f >= 1801.80)
    )
    def sejour_entrepreneur(self):
        self.declare(Fact(eligibilite='P014'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'invest' in m),
        Profil(invest_funds=MATCH.f),
        TEST(lambda f: f >= 30000),
        Profil(studies_degree=MATCH.d),
        TEST(lambda d: d in ['master', 'doctorat'])
    )
    def passeport_talent_creation_entreprise(self):
        self.declare(Fact(eligibilite='P021'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'invest' in m),
        Profil(invest_hasBP=True)
    )
    def passeport_talent_projet_innovant(self):
        self.declare(Fact(eligibilite='P022'))

    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'invest' in m),
        Profil(invest_funds=MATCH.f),
        TEST(lambda f: f >= 300000)
    )
    def passeport_talent_investisseur(self):
        self.declare(Fact(eligibilite='P023'))
        
    # ======================== AES – Mé8ers en tension ========================
    # TODO: Ajout des documents
    @Rule(
        Profil(yearsResidence=MATCH.y),
        TEST(lambda y: y in ['3-5', '>5']),
        Profil(AES_profession = MATCH.p),
        TEST(lambda p : p not in ["aucun", "non", "autre"]),
    )
    def passeport_talent_investisseur2(self):
        self.declare(Fact(eligibilite='P056'))
    

    # ======================== VISITEUR ========================
    @Rule(
        Profil(motifPrincipal=MATCH.m),
        TEST(lambda m: 'visiteur' in m),
        Profil(visitor_resources=MATCH.r),
        TEST(lambda r: r in ['1200_1426', 'plus_1426'])
    )
    def sejour_visiteur(self):
        self.declare(Fact(eligibilite='P042'))

    # ======================== SITUATIONS SPÉCIALES ========================
    @Rule(
        Profil(specialSituations=MATCH.s),
        TEST(lambda s: 'volontaire' in s)
    )
    def aps_volontariat(self):
        self.declare(Fact(eligibilite='P030'))

    @Rule(
        Profil(specialSituations=MATCH.s),
        TEST(lambda s: 'parentMalade' in s),
        Profil(hasMinorChildren=True)
    )
    def aps_parent_enfant_malade(self):
        self.declare(Fact(eligibilite='P029'))

    @Rule(
        Profil(specialSituations=MATCH.s),
        TEST(lambda s: 'ancienCombattant' in s),
        Profil(resident_integrationOK=True, resident_languageA2=MATCH.l),
        TEST(lambda l: l not in ['pas_de_preuve', "aucun"])
    )
    def resident_ancien_combattant(self):
        self.declare(Fact(eligibilite='P036'))
        
    @Rule(
        Profil(specialSituations=MATCH.s),
        TEST(lambda s: 'ancienCombattant' in s),
        Profil(resident_integrationOK=True, resident_languageA2=MATCH.l),
        TEST(lambda l: l in ['pas_de_preuve', "aucun"])
    )
    def resident_ancien_combattant2(self):
        self.declare(Fact(eligibilite='P0360'))

    # ======================== RÉSIDENCE LONGUE DURÉE ========================
    @Rule(
        Profil(yearsResidence='>5', resident_integrationOK=True, resident_languageA2=MATCH.l),
        TEST(lambda l: l not in ['pas_de_preuve',"aucun"])
    )
    def resident_longue_duree_ue(self):
        self.declare(Fact(eligibilite='P032'))
        
    @Rule(
        Profil(yearsResidence='>5', resident_integrationOK=True, resident_languageA2=MATCH.l),
        TEST(lambda l: l in ['pas_de_preuve',"aucun"])
    )
    def resident_longue_duree_ue2(self):
        self.declare(Fact(eligibilite='P032'))

    @Rule(
        Profil(currentPermit=MATCH.p),
        TEST(lambda p: p in ['resident_10ans','resident_ld_ue', 'resident_permanent']),
        Profil(resident_integrationOK=True, resident_longAbsence=False)
    )
    def resident_permanent(self):
        self.declare(Fact(eligibilite='P035'))

    @Rule(
        Profil(currentPermit=MATCH.p),
        TEST(lambda p: p in ['resident_10ans', 'resident_ld_ue', 'resident_permanent'])
    )
    def sejour_retraite(self):
        self.declare(Fact(eligibilite='P044'))

    @Rule(
        Profil(currentPermit=MATCH.p),
        TEST(lambda p: p.startswith('csp_')),
        Profil(pluri_integrationOK=True)
    )
    def sejour_pluriannuelle(self):
        self.declare(Fact(eligibilite='P015'))

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
            if "_" in v:
                out[key] = v
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


# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == "__main__":
    moteur = MoteurEligibilite()
    moteur.reset()  # Réinitialiser le moteur
    moteur.run()    # Lancer la simulation