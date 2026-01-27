import re
from difflib import SequenceMatcher

def calculer_score_auto(cv_text: str, offre: dict, projets_keywords: list = None) -> dict:
    """
    Calcule un score automatique à partir du CV et d'une offre.
    Optionnel: projets_keywords pour matching plus précis sur projets.
    Retourne un dictionnaire avec score final et si le seuil est dépassé.
    """
    # --- Initialisation ---
    score = 0
    max_score = 100
    w_skills = offre.get("w_skills", 0.4)
    w_exp = offre.get("w_exp", 0.3)
    w_edu = offre.get("w_edu", 0.2)
    w_proj = offre.get("w_proj", 0.1)
    threshold = offre.get("threshold", 60)

    # --- 1️⃣ Compétences techniques ---
    if offre.get("tech_skills"):
        for skill in offre["tech_skills"]:
            if skill.lower() in cv_text.lower():
                score += 10 * w_skills

    # --- 2️⃣ Compétences comportementales ---
    if offre.get("soft_skills"):
        for skill in offre["soft_skills"]:
            if skill.lower() in cv_text.lower():
                score += 5 * w_skills

    # --- 3️⃣ Langues ---
    if offre.get("langs_lvl"):
        for lang, lvl in offre["langs_lvl"].items():
            if lang.lower() in cv_text.lower():
                score += 5  # simple match, pondérable selon niveau

    # --- 4️⃣ Formation / niveau d'études ---
    if offre.get("education_level"):
        if offre["education_level"].lower() in cv_text.lower():
            score += 20 * w_edu

    # --- 5️⃣ Expérience ---
    exp_required = offre.get("exp_required_years", 0)
    match = re.search(r"\b(\d+)\s+ans\b", cv_text.lower())
    if match:
        exp_cv = int(match.group(1))
        exp_score = min(exp_cv / max(exp_required, 1), 1) * 20 * w_exp
        score += exp_score

    # --- 6️⃣ Analyse des projets / missions ---
    texte_projet = " ".join(
        filter(None, [
            offre.get("mission", ""),
            offre.get("activities_public", ""),
            offre.get("goals", "")
        ])
    )
    if texte_projet:
        simil = SequenceMatcher(None, cv_text.lower(), texte_projet.lower()).ratio()
        score += simil * 20 * w_proj

    # --- 7️⃣ Matching mots-clés projets spécifiques ---
    if projets_keywords:
        for keyword in projets_keywords:
            if keyword.lower() in cv_text.lower():
                score += 2  # bonus par mot-clé spécifique, pondération simple
        # Limiter score pour ne pas dépasser max_score
        score = min(score, max_score)

    # --- 8️⃣ Limitation score max 100 ---
    score = min(round(score, 2), max_score)

    # --- 9️⃣ Vérification seuil ---
    passed_threshold = score >= threshold

    return {
        "score": score,
        "passed_threshold": passed_threshold
    }



