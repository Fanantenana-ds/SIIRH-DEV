# import re
# from difflib import SequenceMatcher

# def calculer_score_auto(cv_text: str, offre: dict, projets_keywords: list = None) -> dict:
#     """
#     Calcule un score automatique à partir du CV et d'une offre.
#     Optionnel: projets_keywords pour matching plus précis sur projets.
#     Retourne un dictionnaire avec score final et si le seuil est dépassé.
#     """
#     # --- Initialisation ---
#     score = 0
#     max_score = 100
#     w_skills = offre.get("w_skills", 0.4)
#     w_exp = offre.get("w_exp", 0.3)
#     w_edu = offre.get("w_edu", 0.2)
#     w_proj = offre.get("w_proj", 0.1)
#     threshold = offre.get("threshold", 60)

#     # --- 1️⃣ Compétences techniques ---
#     if offre.get("tech_skills"):
#         for skill in offre["tech_skills"]:
#             if skill.lower() in cv_text.lower():
#                 score += 10 * w_skills

#     # --- 2️⃣ Compétences comportementales ---
#     if offre.get("soft_skills"):
#         for skill in offre["soft_skills"]:
#             if skill.lower() in cv_text.lower():
#                 score += 5 * w_skills

#     # --- 3️⃣ Langues ---
#     if offre.get("langs_lvl"):
#         for lang, lvl in offre["langs_lvl"].items():
#             if lang.lower() in cv_text.lower():
#                 score += 5  # simple match, pondérable selon niveau

#     # --- 4️⃣ Formation / niveau d'études ---
#     if offre.get("education_level"):
#         if offre["education_level"].lower() in cv_text.lower():
#             score += 20 * w_edu

#     # --- 5️⃣ Expérience ---
#     exp_required = offre.get("exp_required_years", 0)
#     match = re.search(r"\b(\d+)\s+ans\b", cv_text.lower())
#     if match:
#         exp_cv = int(match.group(1))
#         exp_score = min(exp_cv / max(exp_required, 1), 1) * 20 * w_exp
#         score += exp_score

#     # --- 6️⃣ Analyse des projets / missions ---
#     texte_projet = " ".join(
#         filter(None, [
#             offre.get("mission", ""),
#             offre.get("activities_public", ""),
#             offre.get("goals", "")
#         ])
#     )
#     if texte_projet:
#         simil = SequenceMatcher(None, cv_text.lower(), texte_projet.lower()).ratio()
#         score += simil * 20 * w_proj

#     # --- 7️⃣ Matching mots-clés projets spécifiques ---
#     if projets_keywords:
#         for keyword in projets_keywords:
#             if keyword.lower() in cv_text.lower():
#                 score += 2  # bonus par mot-clé spécifique, pondération simple
#         # Limiter score pour ne pas dépasser max_score
#         score = min(score, max_score)

#     # --- 8️⃣ Limitation score max 100 ---
#     score = min(round(score, 2), max_score)

#     # --- 9️⃣ Vérification seuil ---
#     passed_threshold = score >= threshold

#     return {
#         "score": score,
#         "passed_threshold": passed_threshold
#     }




# app/services/scoring_auto.py - VERSION COMPLÈTE ET AMÉLIORÉE
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

def calculate_cv_score(cv_text: str, offre_description: str = "") -> Dict:
    """Calculer le score d'un CV - VERSION ROBUSTE"""
    
    try:
        if not cv_text or len(cv_text.strip()) < 100:
            logger.warning(f"⚠️ Texte CV trop court ({len(cv_text) if cv_text else 0} caractères), score minimal: 10%")
            return {'score_total': 10, 'details': {'base': 10}}
        
        cv_lower = cv_text.lower()
        
        # Initialiser le score
        score_total = 10  # Score de base
        score_details = {}
        
        logger.info(f"📊 Calcul du score démarré, CV: {len(cv_text)} caractères")
        
        # 1. STRUCTURE DU CV (max 30 points)
        structure_score = 0
        
        sections_to_check = [
            ('experience', r'exp[ée]rience|experience|work|emploi|professional|travail'),
            ('education', r'formation|education|dipl[ôo]me|degree|study|études|academic'),
            ('skills', r'comp[ée]tence|skill|expertise|competence|ability|connaissance'),
            ('contact', r'contact|coordonn[ée]e|email|t[ée]l[ée]phone|address|adresse'),
            ('projects', r'projet|project|r[ée]alisation|achievement|portfolio'),
            ('languages', r'langue|language|idiome|anglais|français')
        ]
        
        found_sections = []
        for section_name, pattern in sections_to_check:
            if re.search(pattern, cv_lower):
                structure_score += 5
                found_sections.append(section_name)
        
        score_details['structure'] = min(structure_score, 30)
        score_total += score_details['structure']
        logger.info(f"   🏗️  Structure ({len(found_sections)} sections): {score_details['structure']} points")
        
        # 2. INFORMATIONS DE CONTACT (max 25 points)
        contact_score = 0
        
        # Email
        if re.search(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-zA-Z]{2,}', cv_text, re.IGNORECASE):
            contact_score += 10
            logger.info(f"   📧 Email présent: +10")
        
        # Téléphone
        if re.search(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}', cv_text) or \
           re.search(r'\+261\s*[3]\s*\d{2}\s*\d{3}\s*\d{2}', cv_text):
            contact_score += 10
            logger.info(f"   📞 Téléphone présent: +10")
        
        # Nom complet
        if re.search(r'[A-ZÀ-Ÿ][a-zA-ZÀ-ÿ]+\s+[A-ZÀ-Ÿ][a-zA-ZÀ-ÿ]+', cv_text):
            contact_score += 5
            logger.info(f"   👤 Nom complet détecté: +5")
        
        score_details['contact'] = min(contact_score, 25)
        score_total += score_details['contact']
        
        # 3. COMPÉTENCES TECHNIQUES (max 25 points)
        skills_score = 0
        
        # Liste étendue de compétences techniques
        technical_skills = [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby',
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
            'spring', 'laravel', 'postgresql', 'mysql', 'mongodb', 'sql', 'oracle',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'jenkins',
            'machine learning', 'data science', 'ai', 'artificial intelligence',
            'big data', 'pandas', 'numpy', 'tensorflow', 'pytorch',
            'agile', 'scrum', 'devops', 'ci/cd', 'tdd', 'bdd'
        ]
        
        found_skills = []
        for skill in technical_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', cv_lower):
                skills_score += 1
                found_skills.append(skill)
        
        score_details['skills'] = min(skills_score, 25)
        score_total += score_details['skills']
        logger.info(f"   🔧 Compétences techniques ({len(found_skills)}): {score_details['skills']} points")
        
        # 4. EXPÉRIENCE PROFESSIONNELLE (max 20 points)
        experience_score = 0
        
        # Chercher années d'expérience
        exp_patterns = [
            r'(\d+)\s*(?:an|ann[ée]e|year)s?\s+d\'?exp[ée]rience',
            r'exp[ée]rience\s+de\s+(\d+)\s*(?:an|ann[ée]e|year)',
            r'(\d+)\s*(?:an|ann[ée]e|year)s?\s+(?:d\'exp|exp[ée]rience)'
        ]
        
        for pattern in exp_patterns:
            exp_match = re.search(pattern, cv_lower)
            if exp_match:
                try:
                    years = int(exp_match.group(1))
                    experience_score += min(years * 3, 15)  # 3 points par année, max 15
                    logger.info(f"   📅 {years} ans d'expérience: +{min(years * 3, 15)}")
                    break
                except:
                    pass
        
        # Si pas d'années précises mais mention d'expérience
        if experience_score == 0 and re.search(r'exp[ée]rience|experience', cv_lower):
            experience_score += 5
            logger.info(f"   📅 Expérience mentionnée: +5")
        
        # Postes précédents
        job_titles = [
            'ingénieur', 'engineer', 'développeur', 'developer', 'analyste', 'analyst',
            'consultant', 'manager', 'chef de projet', 'lead', 'senior', 'junior',
            'architect', 'data scientist', 'devops', 'qa', 'test', 'administrateur'
        ]
        
        job_count = 0
        for title in job_titles:
            if re.search(r'\b' + re.escape(title) + r'\b', cv_lower):
                job_count += 1
        
        experience_score += min(job_count * 2, 5)  # 2 points par poste, max 5
        
        score_details['experience'] = min(experience_score, 20)
        score_total += score_details['experience']
        
        # 5. FORMATION (max 20 points)
        education_score = 0
        
        education_levels = [
            ('bac', 5), ('baccalaureat', 5), ('bts', 10), ('dut', 10),
            ('licence', 15), ('bachelor', 15), ('master', 20), ('mastère', 20),
            ('ingénieur', 25), ('engineer', 25), ('doctorat', 30), ('phd', 30)
        ]
        
        for level, points in education_levels:
            if re.search(r'\b' + re.escape(level) + r'\b', cv_lower):
                education_score = max(education_score, points)
                logger.info(f"   🎓 Niveau {level}: +{points}")
                break
        
        # Si pas de niveau précis mais mention d'éducation
        if education_score == 0 and re.search(r'formation|education|dipl[ôo]me', cv_lower):
            education_score += 5
        
        score_details['education'] = min(education_score, 20)
        score_total += score_details['education']
        
        # 6. MATCHING AVEC L'OFFRE (max 30 points si offre disponible)
        matching_score = 0
        
        if offre_description and len(offre_description.strip()) > 20:
            offre_lower = offre_description.lower()
            
            # Déterminer le type de poste
            poste_type = ""
            if any(word in offre_lower for word in ['data', 'scientist', 'analyst', 'analytics']):
                poste_type = 'data'
                required_skills = ['python', 'sql', 'machine learning', 'data', 'statistics', 'r', 'pandas', 'numpy']
            elif any(word in offre_lower for word in ['dev', 'développeur', 'developer', 'programmeur']):
                poste_type = 'dev'
                required_skills = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'git', 'docker']
            elif any(word in offre_lower for word in ['test', 'qa', 'quality']):
                poste_type = 'test'
                required_skills = ['testing', 'qa', 'automation', 'selenium', 'junit', 'testng']
            else:
                poste_type = 'general'
                required_skills = ['python', 'java', 'javascript', 'react', 'sql', 'git', 'agile']
            
            matching_skills = []
            for skill in required_skills:
                if skill in offre_lower and skill in cv_lower:
                    matching_skills.append(skill)
                    matching_score += 3
            
            score_details['matching'] = min(matching_score, 30)
            score_total += score_details['matching']
            logger.info(f"   🎯 Matching offre ({poste_type}, {len(matching_skills)} compétences): {score_details['matching']} points")
        else:
            score_details['matching'] = 0
            logger.info(f"   ⚠️  Pas d'offre pour matching")
        
        # Limiter le score entre 10 et 100
        score_total = max(10, min(100, score_total))
        
        logger.info(f"📊 Score final: {score_total}%")
        logger.info(f"   Détails: {score_details}")
        
        return {
            'score_total': score_total,
            'details': score_details
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur calcul score: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {'score_total': 10, 'details': {'error': str(e)}}

# Fonctions de compatibilité
def calculer_score_auto(cv_text: str, offre_description: str = "") -> Dict:
    """Alias pour compatibilité"""
    return calculate_cv_score(cv_text, offre_description)

def calculate_score_auto(*args, **kwargs):
    """Alias supplémentaire"""
    return calculate_cv_score(*args, **kwargs)

def extract_skills_from_text(text: str) -> list:
    """Extraire les compétences techniques d'un texte"""
    common_skills = [
        'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
        'node.js', 'django', 'flask', 'fastapi', 'spring', 'laravel',
        'postgresql', 'mysql', 'mongodb', 'redis', 'oracle',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git',
        'machine learning', 'data science', 'data analysis', 'ai',
        'agile', 'scrum', 'devops', 'ci/cd'
    ]
    
    found_skills = []
    for skill in common_skills:
        if skill in text.lower():
            found_skills.append(skill)
    
    return found_skills