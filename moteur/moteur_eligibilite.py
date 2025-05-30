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

    @Rule(Profil(family_link='mariage', family_community=True, valid_visa_or_residence=True))
    def sejour_vpf_conjoint_francais(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Conjoint de citoyen français'))

    @Rule(Profil(family_link='pacs', family_community=True, valid_visa_or_residence=True))
    def sejour_vpf_pacs(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Partenaire Pacsé avec un Français'))

    @Rule(Profil(family_link='parentEnfFr', french_minor_child_in_france=True, supporting_child=True, valid_visa_or_residence=True))
    def sejour_vpf_parent_enfant_francais(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Parent d\'enfant français mineur'))

    @Rule(Profil(family_link='regroup', entered_france_as_minor_family_reunification=True))
    def sejour_vpf_reunification_mineur(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Jeune adulte entré par regroupement familial'))

    @Rule(Profil(family_link='famUE', spouse_of_eu_long_term_resident=True, resided_in_eu_country=True, own_resources=True, health_insurance=True))
    def sejour_vpf_eu_long_term_resident(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Membre de famille d\'un étranger résident UE'))

    @Rule(Profil(born_or_raised_in_france=True, specific_residence_and_schooling_conditions=True))
    def sejour_vpf_jeune_france(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Jeune né ou entré mineur en France'))

    @Rule(
        Profil(work_accident_pension=True, disability_rate=MATCH.dr),
        TEST(lambda dr: dr >= 20 if dr else False)
    )
    def sejour_vpf_pension_accident(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Bénéficiaire pension accident travail'))

    @Rule(
        Profil(uninterrupted_work_in_approved_orgs=True, minimum_duration=MATCH.md),
        TEST(lambda md: md >= 3 if md else False)
    )
    def sejour_vpf_travail_solidaire(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Travail solidaire'))

    @Rule(Profil(humanitarian_reasons=True))
    def sejour_vpf_humanitaire(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Raisons humanitaires'))

    @Rule(Profil(victim_of_domestic_violence=True, protection_order=True))
    def sejour_vpf_violence_domestique(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Victime violence domestique'))

    @Rule(Profil(victim_of_human_trafficking=True, filed_complaint=True))
    def sejour_vpf_traite(self):
        self.declare(Fact(eligibilite='Carte de Séjour "vie privée et familiale" - Victime traite ou proxénétisme'))

    # ======================== TRAVAIL ========================
    @Rule(Profil(work_contract='CDI', work_permit=True))
    def sejour_salarie_cdi(self):
        self.declare(Fact(eligibilite='Carte de Séjour "salarié"'))

    @Rule(Profil(work_contract='CDD', work_permit=True))
    def sejour_salarie_cdd(self):
        self.declare(Fact(eligibilite='Carte de Séjour "salarié"'))

    @Rule(
        Profil(work_contract='detache', seniority_at_least_6_months=True, salary_above_threshold=MATCH.s),
        TEST(lambda s: s >= 1801.8 if s else False)
    )
    def sejour_ict(self):
        self.declare(Fact(eligibilite='Carte de Séjour "salarié détaché ICT"'))

    @Rule(Profil(work_contract='saisonnier', seasonal_work_limit=True, residence_outside_france=True, approved_seasonal_contract=True))
    def sejour_saisonnier(self):
        self.declare(Fact(eligibilite='Carte de Séjour "travailleur saisonnier"'))

    @Rule(Profil(temporary_work_contract=True, work_permit=True, valid_visa_for_temporary_work=True))
    def sejour_travailleur_temporaire(self):
        self.declare(Fact(eligibilite='Carte de Séjour "travailleur temporaire"'))

    # ======================== ÉTUDES ========================
    @Rule(
        Profil(studies_status='etudiant', higher_education_enrollment=True, monthly_income_above_threshold=MATCH.i),
        TEST(lambda i: i >= 615 if i else False)
    )
    def sejour_etudiant(self):
        self.declare(Fact(eligibilite='Visa "étudiant" / Carte de Séjour "étudiant"'))

    @Rule(Profil(studies_status='stagiaire', tripartite_internship_agreement=True, internship_over_3_months=True))
    def sejour_stagiaire(self):
        self.declare(Fact(eligibilite='Visa ou Carte de Séjour "stagiaire"'))

    @Rule(Profil(studies_status='chercheur', approved_host_organization_agreement=True))
    def sejour_chercheur(self):
        self.declare(Fact(eligibilite='Passeport talent – chercheur'))

    @Rule(
        Profil(eu_mobility_program_student=True, enrolled_in_mobility_program=True, monthly_income_above_threshold=MATCH.i),
        TEST(lambda i: i >= 615 if i else False)
    )
    def sejour_mobilite_etudiant(self):
        self.declare(Fact(eligibilite='Carte de Séjour "étudiant - programme de mobilité"'))

    # ======================== INVEST / TALENT ========================
    @Rule(Profil(entrepreneur_or_self_employed=True, registered_business_activity=True, viable_activity=True, sufficient_resources=True))
    def sejour_entrepreneur(self):
        self.declare(Fact(eligibilite='Carte de Séjour "entrepreneur/profession libérale"'))

    @Rule(
        Profil(diploma_master_or_higher=True, employment_contract_over_3_months=True, salary_above_threshold=MATCH.s),
        TEST(lambda s: s >= 43243 if s else False)
    )
    def passeport_talent_salarie(self):
        self.declare(Fact(eligibilite='Passeport talent – salarié qualifié'))

    @Rule(
        Profil(hired_by_innovative_company=True, r_and_d_related_contract=True, salary_above_threshold=MATCH.s),
        TEST(lambda s: s >= 43243 if s else False)
    )
    def passeport_talent_recrute(self):
        self.declare(Fact(eligibilite='Passeport talent – recrutement entreprise innovante'))

    @Rule(
        Profil(bachelor_degree_or_experience=True, contract_one_year_or_more=True, salary_above_threshold=MATCH.s),
        TEST(lambda s: s >= 53836.5 if s else False)
    )
    def passeport_talent_carte_bleue(self):
        self.declare(Fact(eligibilite='Passeport talent – carte bleue européenne'))

    @Rule(
        Profil(seconded_within_group=True, seniority_at_least_3_months=True, salary_above_threshold=MATCH.s),
        TEST(lambda s: s >= 38918.88 if s else False)
    )
    def passeport_talent_mission(self):
        self.declare(Fact(eligibilite='Passeport talent – salarié en mission'))

    @Rule(Profil(diploma_master_or_higher_or_experience=True, serious_business_creation_plan=True))
    def passeport_talent_creation(self):
        self.declare(Fact(eligibilite='Passeport talent – création d’entreprise'))

    @Rule(Profil(recognized_innovative_project=True))
    def passeport_talent_projet(self):
        self.declare(Fact(eligibilite='Passeport talent – projet innovant'))

    @Rule(Profil(investment_above_threshold=True, job_creation_or_preservation=True))
    def passeport_talent_investisseur(self):
        self.declare(Fact(eligibilite='Passeport talent – investisseur'))

    @Rule(
        Profil(legal_representative=True, contract_over_3_months=True, salary_above_threshold=MATCH.s),
        TEST(lambda s: s >= 64864.8 if s else False)
    )
    def passeport_talent_mandataire(self):
        self.declare(Fact(eligibilite='Passeport talent – mandataire social'))

    @Rule(Profil(artistic_or_cultural_profession=True, sufficient_resources=True))
    def passeport_talent_artiste(self):
        self.declare(Fact(eligibilite='Passeport talent – profession artistique et culturelle'))

    @Rule(Profil(international_recognition=True, intention_to_work_in_france=True))
    def passeport_talent_renomme(self):
        self.declare(Fact(eligibilite='Passeport talent – personne de renommée internationale'))

    @Rule(Profil(spouse_or_minor_child_of_passport_holder=True))
    def passeport_talent_famille(self):
        self.declare(Fact(eligibilite='Passeport talent (famille)'))

    # ======================== VISITEUR ========================
    @Rule(
        Profil(stay_over_3_months=True, sufficient_annual_income=MATCH.i, health_insurance_coverage=True, no_employment=True),
        TEST(lambda i: i >= 17115.69 if i else False)
    )
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
    @Rule(Profil(residency_at_least_5_years=True, health_insurance=True, income_above_smic=True, language_level_a2=True))
    def carte_resident_ld_ue(self):
        self.declare(Fact(eligibilite='Carte de Résident Longue Durée - UE'))

    @Rule(Profil(married_to_french_for_at_least_3_years=True, community_of_life=True, language_requirements=True))
    def carte_resident_epoux(self):
        self.declare(Fact(eligibilite='Carte de Résident - Époux de Français'))

    # ======================== NATURALISATION ========================
    @Rule(
        Profil(ancestor_of_french_citizen=True, regular_residence_at_least_25_years=MATCH.y),
        TEST(lambda y: y >= 25)
    )
    def naturalisation_ascendant(self):
        self.declare(Fact(eligibilite='Naturalisation par Déclaration – Ascendant'))

    @Rule(Profil(sibling_of_french_citizen=True, residence_in_france_since_age_16=True))
    def naturalisation_fratrie(self):
        self.declare(Fact(eligibilite='Naturalisation par Déclaration – Fratrie'))

    @Rule(Profil(married_to_french_citizen_for_at_least_4_years=True, community_of_life=True, language_b1_proficiency=True))
    def naturalisation_mariage(self):
        self.declare(Fact(eligibilite='Naturalisation par Déclaration – Mariage'))

    @Rule(Profil(residency_at_least_5_years=True, integration_criteria=True, language_b1_proficiency=True))
    def naturalisation_decret(self):
        self.declare(Fact(eligibilite='Naturalisation par Décret'))

    # ======================== AUTRES ========================
    @Rule(Profil(eu_citizen_working_professionally=True))
    def sejour_eu_travailleur(self):
        self.declare(Fact(eligibilite='Carte de Séjour pour Européen - Travailleur'))

    @Rule(Profil(eu_citizen_enrolled_in_studies=True, health_insurance=True))
    def sejour_eu_etudiant(self):
        self.declare(Fact(eligibilite='Carte de Séjour pour Européen - Étudiant'))

    @Rule(Profil(eu_citizen_retired_or_inactive=True, health_insurance=True))
    def sejour_eu_retraite(self):
        self.declare(Fact(eligibilite='Carte de Séjour pour Européen - Retraité ou inactif'))

    @Rule(Profil(family_member_of_eu_citizen=True))
    def sejour_eu_famille(self):
        self.declare(Fact(eligibilite='Carte de Séjour pour Européen - Membre de la famille'))

    @Rule(Profil(minor_foreign_resident_in_france=True, parent_or_guardian_with_valid_title=True))
    def document_mineur(self):
        self.declare(Fact(eligibilite='Document de Circulation pour Mineur Étranger'))

    # ======================== DURÉE DE RÉSIDENCE ========================
    @Rule(Profil(yearsResidence=MATCH.y), TEST(lambda y: y >= 10))
    def sejour_longue_residence(self):
        self.declare(Fact(eligibilite='Carte de séjour pour résidence habituelle de plus de 10 ans'))

    # ======================== CERTIFICATS ALGÉRIENS ========================
    @Rule(
        Profil(nationality_sim='DZ', alg1_motif=MATCH.m),
        TEST(lambda m: m in ['mariage', 'parent', 'etat_sante', 'vie_priv'])
    )
    def certificat_alg_1an(self):
        self.declare(Fact(eligibilite='Certificat algérien 1 an'))

    @Rule(
        Profil(nationality_sim='DZ', alg10_type=MATCH.t),
        TEST(lambda t: t in ['res10', 'famViePriv', 'francophone', 'rente'])
    )
    def certificat_alg_10ans(self):
        self.declare(Fact(eligibilite='Certificat algérien 10 ans'))

    # ======================== PLURIANNUELLE ========================
    @Rule(Profil(previous_temporary_card=True, continuing_conditions=True, attended_cir=True, republican_principles=True))
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
