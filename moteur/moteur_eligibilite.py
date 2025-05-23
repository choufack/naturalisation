from flask import Flask, render_template_string, request
from experta import *

app = Flask(__name__)

class Profil(Fact):
    pass

class MoteurEligibilite(KnowledgeEngine):
    @Rule(Profil(mariage_francais_depuis_4_ans=True, niveau_francais=True))
    def nationalite_par_mariage(self):
        self.declare(Fact(eligibilite="Nationalité française par mariage avec un Français"))

    @Rule(Profil(frere_ou_soeur_francais=True, residence_10_ans=True))
    def nationalite_par_fratrie(self):
        self.declare(Fact(eligibilite="Nationalité française par lien de fratrie et scolarité"))

    @Rule(Profil(residence_france_plus_5_ans=True, niveau_francais=True))
    def nationalite_par_naturalisation(self):
        self.declare(Fact(eligibilite="Naturalisation française par résidence de 5 ans"))

    @Rule(Profil(ascendant_francais=True))
    def nationalite_par_ascendant(self):
        self.declare(Fact(eligibilite="Nationalité française en tant qu’ascendant d’un Français"))

    @Rule(Profil(parent_enfant_francais=True))
    def sejour_parent_enfant_francais(self):
        self.declare(Fact(eligibilite="Carte de séjour 'vie privée et familiale' – parent d’un enfant français"))

    @Rule(Profil(conjoint_francais=True))
    def sejour_conjoint_francais(self):
        self.declare(Fact(eligibilite="Carte de séjour 'vie privée et familiale' – conjoint de Français"))

    @Rule(Profil(pacs_francais=True, vie_commune_1_an=True))
    def sejour_pacs(self):
        self.declare(Fact(eligibilite="Carte de séjour 'vie privée et familiale' – partenaire Pacsé avec un Français"))

    @Rule(Profil(entree_jeune_avant_13_ans=True, residence_continue=True))
    def sejour_jeune_majeur(self):
        self.declare(Fact(eligibilite="Carte de séjour 'vie privée et familiale' – jeune entré avant 13 ans"))

    @Rule(Profil(aide_sociale=True))
    def sejour_ase(self):
        self.declare(Fact(eligibilite="Carte de séjour 'vie privée et familiale' – jeune pris en charge par l’ASE"))

    @Rule(Profil(ne_en_france=True, residence_8_ans=True, scolarite_5_ans=True))
    def sejour_ne_en_france(self):
        self.declare(Fact(eligibilite="Carte de séjour 'vie privée et familiale' – né et scolarisé en France"))

    @Rule(Profil(sante_grave=True))
    def sejour_sante(self):
        self.declare(Fact(eligibilite="Carte de séjour pour soins médicaux en France"))

    @Rule(Profil(residence_france_plus_10_ans=True))
    def sejour_longue_residence(self):
        self.declare(Fact(eligibilite="Carte de séjour pour résidence habituelle de plus de 10 ans"))

    @Rule(Profil(liens_personnels_familiaux=True))
    def sejour_liens_familiaux(self):
        self.declare(Fact(eligibilite="Carte de séjour pour liens personnels et familiaux importants"))

    @Rule(Profil(victime_traite=True))
    def sejour_protection(self):
        self.declare(Fact(eligibilite="Carte de séjour – protection des victimes de traite ou proxénétisme"))

    @Rule(Profil(promesse_embauche=True, vls_ts=True))
    def sejour_salarie(self):
        self.declare(Fact(eligibilite="Carte de séjour 'salarié' ou 'travailleur temporaire'"))

    @Rule(Profil(travail_saisonnier=True))
    def sejour_saisonnier(self):
        self.declare(Fact(eligibilite="Carte de séjour 'travailleur saisonnier'"))

    @Rule(Profil(diplome_francais=True, motive_travail=True))
    def sejour_recherche_emploi(self):
        self.declare(Fact(eligibilite="Carte de séjour 'recherche d’emploi / création d’entreprise'"))

    @Rule(Profil(etudiant=True))
    def sejour_etudiant(self):
        self.declare(Fact(eligibilite="Carte de séjour 'étudiant'"))

    @Rule(Profil(stage=True))
    def sejour_stagiaire(self):
        self.declare(Fact(eligibilite="Carte de séjour 'stagiaire'"))

    @Rule(Profil(au_pair=True))
    def sejour_au_pair(self):
        self.declare(Fact(eligibilite="Carte de séjour 'jeune au pair'"))

    @Rule(Profil(visiteur=True))
    def sejour_visiteur(self):
        self.declare(Fact(eligibilite="Carte de séjour 'visiteur'"))

    @Rule(Profil(entrepreneur=True))
    def sejour_entrepreneur(self):
        self.declare(Fact(eligibilite="Carte de séjour 'entrepreneur / profession libérale'"))

    @Rule(Profil(passeport_talent=True))
    def sejour_passeport_talent(self):
        self.declare(Fact(eligibilite="Carte de séjour 'passeport talent' (toutes catégories)"))

    @Rule(Profil(passeport_talent_famille=True))
    def sejour_passeport_talent_famille(self):
        self.declare(Fact(eligibilite="Carte de séjour 'passeport talent – famille'"))

    @Rule(Profil(ict_detache=True))
    def sejour_ict(self):
        self.declare(Fact(eligibilite="Carte de séjour 'salarié détaché ICT'"))

    @Rule(Profil(volontariat=True))
    def sejour_volontaire(self):
        self.declare(Fact(eligibilite="Autorisation de séjour pour mission de volontariat"))

    @Rule(Profil(parent_enfant_malade=True))
    def sejour_parent_enfant_malade(self):
        self.declare(Fact(eligibilite="Autorisation provisoire de séjour – parent d’enfant malade"))

    @Rule(Profil(certificat_residence_algerien_1an=True))
    def certificat_algerien_1an(self):
        self.declare(Fact(eligibilite="Certificat de résidence algérien – 1 an"))

    @Rule(Profil(certificat_residence_algerien_10ans=True))
    def certificat_algerien_10ans(self):
        self.declare(Fact(eligibilite="Certificat de résidence algérien – 10 ans"))

    @Rule(Profil(certificat_retraite_algerien=True))
    def certificat_retraite_algerien(self):
        self.declare(Fact(eligibilite="Certificat de résidence – retraité algérien"))

    @Rule(Profil(carte_resident=True))
    def carte_resident(self):
        self.declare(Fact(eligibilite="Carte de résident"))

    @Rule(Profil(carte_resident_ue=True))
    def carte_resident_ue(self):
        self.declare(Fact(eligibilite="Carte de résident de longue durée – UE"))

    @Rule(Profil(carte_resident_permanent=True))
    def carte_resident_permanent(self):
        self.declare(Fact(eligibilite="Carte de résident permanent"))

    @Rule(Profil(enfant_ne_en_france=True, res_5_ans_depuis_11=True))
    def nationalite_enfant_france(self):
        self.declare(Fact(eligibilite="Nationalité française – enfant né en France"))

    @Rule(Profil(adoption=True))
    def nationalite_adoption(self):
        self.declare(Fact(eligibilite="Nationalité française – enfant adopté"))

    @Rule(Profil(enfant_recueilli=True))
    def nationalite_recueilli(self):
        self.declare(Fact(eligibilite="Nationalité française – enfant recueilli par un Français"))

    @Rule(Profil(reintegration_declaration=True))
    def nationalite_reintegration_decl(self):
        self.declare(Fact(eligibilite="Réintégration dans la nationalité par déclaration"))

    @Rule(Profil(reintegration_decret=True))
    def nationalite_reintegration_decret(self):
        self.declare(Fact(eligibilite="Réintégration dans la nationalité par décret"))

    @Rule(Profil(etudiant_ne_en_france_major=True))
    def nationalite_etudiant_major(self):
        self.declare(Fact(eligibilite="Nationalité française automatique à 18 ans pour enfant né en France"))

@app.route('/', methods=['GET', 'POST'])
def index():
    resultats = []
    if request.method == 'POST':
        data = {k: (v == 'oui') for k, v in request.form.items()}
        moteur = MoteurEligibilite()
        moteur.reset()
        moteur.declare(Profil(**data))
        moteur.run()
        resultats = [f["eligibilite"] for f in moteur.facts.values() if isinstance(f, Fact) and f.get("eligibilite")]

    return render_template_string("""...HTML FORMULAIRE...""", resultats=resultats)

if __name__ == '__main__':
    app.run(debug=True)
