RULES_MATRIX: List[Dict] = [
    # ------------------------------------------------------------------ #
    #   1. NATIONALITÉ (7)
    # ------------------------------------------------------------------ #
    {
        "label": "Nationalité française par mariage (≥ 4 ans)",
        "cond": lambda p: "famille" in (p.motifPrincipal or [])
        and getattr(p, "family_link", None) == "mariage"
        and getattr(p, "family_yearsMarriage", 0) >= 4
        and getattr(p, "family_community", False),
    },
    {
        "label": "Nationalité française par lien de fratrie et scolarité",
        "cond": lambda p: getattr(p, "frere_ou_soeur_francais", False)
        and getattr(p, "yearsResidence", 0) >= 10,
    },
    {
        "label": "Naturalisation française par résidence de 5 ans",
        "cond": lambda p: getattr(p, "yearsResidence", 0) >= 5
        and getattr(p, "niveau_francais", False),
    },
    {
        "label": "Nationalité française en tant qu’ascendant d’un Français",
        "cond": lambda p: getattr(p, "ascendant_francais", False),
    },
    {
        "label": "Nationalité française – enfant né en France (major 18 ans)",
        "cond": lambda p: getattr(p, "etudiant_ne_en_france_major", False),
    },
    {
        "label": "Nationalité française – enfant adopté",
        "cond": lambda p: getattr(p, "adoption", False),
    },
    {
        "label": "Réintégration dans la nationalité par décret ou déclaration",
        "cond": lambda p: getattr(p, "reintegration_declaration", False)
        or getattr(p, "reintegration_decret", False),
    },
    # ------------------------------------------------------------------ #
    #   2. VIE PRIVÉE & FAMILIALE (10)
    # ------------------------------------------------------------------ #
    {
        "label": "Carte VP&F – conjoint(e) de Français(e)",
        "cond": lambda p: "famille" in (p.motifPrincipal or [])
        and getattr(p, "family_link", None) == "mariage"
        and getattr(p, "family_community", False),
    },
    {
        "label": "Carte VP&F – partenaire Pacsé Français(e)",
        "cond": lambda p: "famille" in (p.motifPrincipal or [])
        and getattr(p, "family_link", None) == "pacs"
        and getattr(p, "family_community", False),
    },
    {
        "label": "Carte VP&F – parent d’un enfant français",
        "cond": lambda p: getattr(p, "family_link", None) == "parentEnfFr",
    },
    {
        "label": "Carte VP&F – regroupement familial",
        "cond": lambda p: getattr(p, "family_link", None) == "regroupement",
    },
    {
        "label": "Carte VP&F – membre de famille citoyen UE/EEE",
        "cond": lambda p: getattr(p, "family_link", None) == "famUE",
    },
    {
        "label": "Carte VP&F – jeune entré avant 13 ans",
        "cond": lambda p: getattr(p, "entree_jeune_avant_13_ans", False)
        and getattr(p, "residence_continue", False),
    },
    {
        "label": "Carte VP&F – jeune pris en charge par l’ASE",
        "cond": lambda p: getattr(p, "aide_sociale", False),
    },
    {
        "label": "Carte VP&F – né et scolarisé en France",
        "cond": lambda p: getattr(p, "ne_en_france", False)
        and getattr(p, "scolarite_5_ans", False)
        and getattr(p, "residence_8_ans", False),
    },
    {
        "label": "Carte VP&F – liens personnels et familiaux importants",
        "cond": lambda p: getattr(p, "liens_personnels_familiaux", False),
    },
    {
        "label": "Carte VP&F – vie privée & familiale (10 ans de résidence)",
        "cond": lambda p: getattr(p, "yearsResidence", 0) >= 10,
    },
    # ------------------------------------------------------------------ #
    #   3. TRAVAIL / RECHERCHE D’EMPLOI (8)
    # ------------------------------------------------------------------ #
    {
        "label": "Carte salarié (CDI/CDD + autorisation)",
        "cond": lambda p: "travail" in (p.motifPrincipal or [])
        and getattr(p, "work_contract", None) in {"CDI", "CDD"}
        and getattr(p, "work_permit", False),
    },
    {
        "label": "Carte salarié détaché ICT",
        "cond": lambda p: getattr(p, "work_contract", None) == "detache",
    },
    {
        "label": "Carte travailleur saisonnier",
        "cond": lambda p: getattr(p, "work_contract", None) == "saisonnier",
    },
    {
        "label": "Carte recherche d’emploi / création d’entreprise",
        "cond": lambda p: getattr(p, "diplome_francais", False)
        and getattr(p, "motive_travail", False),
    },
    {
        "label": "Carte entrepreneur / profession libérale",
        "cond": lambda p: "invest" in (p.motifPrincipal or [])
        and getattr(p, "invest_registered", False)
        and not getattr(p, "invest_hasBP", False),
    },
    {
        "label": "Passeport talent – création d’entreprise (≥ 30 000 €)",
        "cond": lambda p: "invest" in (p.motifPrincipal or [])
        and getattr(p, "invest_registered", False)
        and getattr(p, "invest_hasBP", False)
        and getattr(p, "invest_funds", 0) >= 30000,
    },
    {
        "label": "Passeport talent – salarié qualifié (CDI haut salaire)",
        "cond": lambda p: getattr(p, "work_contract", None) == "CDI"
        and getattr(p, "work_salary", 0) >= 53000,  # seuil 2025
    },
    {
        "label": "Passeport talent – profession artistique ou culturel",
        "cond": lambda p: getattr(p, "specialSituations", []) and "talentArtiste" in p.specialSituations,
    },
    # ------------------------------------------------------------------ #
    #   4. ÉTUDES / STAGIAIRE / CHERCHEUR (3)
    # ------------------------------------------------------------------ #
    {
        "label": "Carte étudiant",
        "cond": lambda p: getattr(p, "studies_status", None) == "etudiant",
    },
    {
        "label": "Carte stagiaire",
        "cond": lambda p: getattr(p, "studies_status", None) == "stagiaire",
    },
    {
        "label": "Passeport talent – chercheur",
        "cond": lambda p: getattr(p, "studies_status", None) == "chercheur",
    },
    # ------------------------------------------------------------------ #
    #   5. PASSEPORT TALENT – FAMILLE (1) & SPORTIF (1)
    # ------------------------------------------------------------------ #
    {
        "label": "Passeport talent – famille",
        "cond": lambda p: getattr(p, "passeport_talent_famille", False),
    },
    {
        "label": "Passeport talent – sportif / entraîneur professionnel",
        "cond": lambda p: getattr(p, "specialSituations", []) and "sportifPro" in p.specialSituations,
    },
    # ------------------------------------------------------------------ #
    #   6. VISITEUR / HUMANITAIRE / SANTÉ / VOLONTARIAT (6)
    # ------------------------------------------------------------------ #
    {
        "label": "Carte visiteur (ressources ≥ SMIC)",
        "cond": lambda p: "visiteur" in (p.motifPrincipal or [])
        and getattr(p, "visitor_resources", "moins_1200") != "moins_1200",
    },
    {
        "label": "Autorisation de séjour – mission de volontariat",
        "cond": lambda p: getattr(p, "specialSituations", []) and "volontaire" in p.specialSituations,
    },
    {
        "label": "Carte soins médicaux (étranger malade)",
        "cond": lambda p: getattr(p, "specialSituations", []) and "medical" in p.specialSituations,
    },
    {
        "label": "APS – parent d’enfant malade",
        "cond": lambda p: getattr(p, "specialSituations", []) and "parentSickChild" in p.specialSituations,
    },
    {
        "label": "Carte – protection des victimes de traite / proxénétisme",
        "cond": lambda p: getattr(p, "specialSituations", []) and "victimeTraite" in p.specialSituations,
    },
    {
        "label": "Carte humanitaire exceptionnelle",
        "cond": lambda p: getattr(p, "specialSituations", []) and "humanitaire" in p.specialSituations,
    },
    # ------------------------------------------------------------------ #
    #   7. CERTIFICATS DE RÉSIDENCE ALGÉRIENS (3)
    # ------------------------------------------------------------------ #
    {
        "label": "Certificat de résidence algérien – 1 an",
        "cond": lambda p: getattr(p, "certificat_residence_algerien_1an", False),
    },
    {
        "label": "Certificat de résidence algérien – 10 ans",
        "cond": lambda p: getattr(p, "certificat_residence_algerien_10ans", False),
    },
    {
        "label": "Certificat de résidence – retraité algérien",
        "cond": lambda p: getattr(p, "certificat_retraite_algerien", False),
    },
    # ------------------------------------------------------------------ #
    #   8. CARTES DE RÉSIDENT (3)
    # ------------------------------------------------------------------ #
    {
        "label": "Carte de résident (10 ans)",
        "cond": lambda p: getattr(p, "carte_resident", False),
    },
    {
        "label": "Carte de résident de longue durée – UE",
        "cond": lambda p: getattr(p, "carte_resident_ue", False),
    },
    {
        "label": "Carte de résident permanent",
        "cond": lambda p: getattr(p, "carte_resident_permanent", False),
    },
    # ------------------------------------------------------------------ #
    #   9. AUTORISATIONS PROVISOIRES (2)
    # ------------------------------------------------------------------ #
    {
        "label": "Autorisation provisoire – ancien combattant / FFI",
        "cond": lambda p: getattr(p, "specialSituations", []) and "ancienCombattant" in p.specialSituations,
    },
    {
        "label": "Titre de voyage – réfugié / protection subsidiaire",
        "cond": lambda p: getattr(p, "specialSituations", []) and "refugie" in p.specialSituations,
    },
]