import re

def calculer_score(cv_text: str, poste: str) -> float:
    """Calcule automatiquement le score d’un candidat à partir de son CV."""

    score = 0

    # Pondération par mots-clés du poste
    mots_cles = {
        "Développeur": ["python", "django", "fastapi", "react", "javascript", "sql"],
        "Comptable": ["comptabilité", "bilan", "excel", "analyse financière", "fiscalité"],
        "RH": ["recrutement", "paie", "gestion du personnel", "formation"],
    }

    # Recherche des mots-clés pertinents
    for mot in mots_cles.get(poste, []):
        if re.search(rf"\b{mot}\b", cv_text.lower()):
            score += 15  # points par mot-clé trouvé

    # Bonus si expérience (ex: “5 ans d’expérience”)
    if re.search(r"\b(\d+)\s+ans\b", cv_text.lower()):
        nb_ans = int(re.search(r"\b(\d+)\s+ans\b", cv_text.lower()).group(1))
        score += min(nb_ans * 2, 20)

    # Score max 100
    return min(score, 100)
