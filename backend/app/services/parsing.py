# from docx import Document
# import pdfplumber
# import re

# # --- 1️⃣ Parser DOCX ---
# def parse_docx(path: str) -> str:
#     doc = Document(path)
#     text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
#     return text

# # --- 2️⃣ Parser PDF ---
# def parse_pdf(path: str) -> str:
#     text = ""
#     with pdfplumber.open(path) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text

# # --- 3️⃣ Extraction automatique d'informations ---
# def extract_info(text: str, project_keywords: list = None) -> dict:
#     """
#     Extrait les informations principales du CV.
#     Optionnel: project_keywords pour extraire mots-clés projets spécifiques.
#     """
#     # Email
#     email = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)

#     # Téléphone
#     phone = re.search(r"\+?\d[\d\s().-]{7,}", text)

#     # Nom/Prénom
#     name_match = re.findall(r"([A-Z][a-z]+)", text)
#     firstname, lastname = (name_match[0], name_match[1]) if len(name_match) >= 2 else (None, None)

#     # Compétences générales
#     skill_keywords = [
#         "Python", "Django", "FastAPI", "React", "SQL", "Docker", "Kubernetes",
#         "Machine Learning", "Data Analysis", "Excel", "Communication", "Leadership"
#     ]
#     skills = [kw for kw in skill_keywords if re.search(rf"\b{kw}\b", text, re.IGNORECASE)]

#     # Diplômes
#     diploma_keywords = ["Licence", "Master", "Doctorat", "Ingénieur", "Bachelor"]
#     diplomes = [d for d in diploma_keywords if re.search(rf"\b{d}\b", text, re.IGNORECASE)]

#     # Langues
#     langues_keywords = ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Malgache"]
#     langues = [l for l in langues_keywords if re.search(rf"\b{l}\b", text, re.IGNORECASE)]

#     # Expérience
#     exp_years_match = re.findall(r"(\d+)\s+(ans|années|an)", text.lower())
#     exp_years = max([int(e[0]) for e in exp_years_match], default=0)

#     # --- Extraction mots-clés projets spécifiques ---
#     project_matches = []
#     if project_keywords:
#         for kw in project_keywords:
#             if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE):
#                 project_matches.append(kw)

#     return {
#         "firstname": firstname,
#         "lastname": lastname,
#         "email": email.group() if email else None,
#         "phone": phone.group() if phone else None,
#         "skills": skills,
#         "diplomes": diplomes,
#         "langues": langues,
#         "exp_years": exp_years,
#         "projects": project_matches,  # nouveauté pour scoring automatique
#         "text": text[:3000],  # résumé pour scoring
#     }

# # --- 4️⃣ Extraction nom + téléphone simple ---
# def extract_name_phone(text: str) -> dict:
#     """
#     Fonction dédiée pour extraire le nom complet et le téléphone.
#     Nécessaire pour upload_service.py afin d'éviter ImportError.
#     """
#     name = None
#     phone = None

#     # Exemple rapide: prend les 2 premiers mots avec majuscule pour nom/prénom
#     name_match = re.findall(r"[A-Z][a-z]+", text)
#     if len(name_match) >= 2:
#         name = f"{name_match[0]} {name_match[1]}"

#     # Téléphone simple
#     phone_match = re.search(r"\+?\d[\d\s().-]{7,}", text)
#     if phone_match:
#         phone = phone_match.group()

#     return {
#         "fullname": name,
#         "phone": phone
#     }
















# app/services/parsing.py - VERSION COMPLÈTE ET FONCTIONNELLE
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class CVExtractor:
    """Extracteur complet pour tous types de CV"""
    
    def __init__(self):
        self.patterns = {
            'email': [
                r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            ],
            'phone': [
                r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}',
                r'\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}',
                r'\+261\s*[3]\s*\d{2}\s*\d{3}\s*\d{2}',
            ],
            'name': [
                r'^[A-ZÀ-Ÿ][A-ZÀ-Ÿa-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)+$',
                r'^[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+$',
                r'^(?:Nom[:\s]*|Prénom[:\s]*|Name[:\s]*)([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s]+)$',
            ]
        }
        
        # Définir les catégories de compétences
        self.skill_categories = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'laravel'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'jenkins', 'ansible'],
            'data': ['machine learning', 'data science', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn'],
            'methodology': ['agile', 'scrum', 'devops', 'ci/cd', 'tdd', 'bdd'],
            'soft': ['communication', 'leadership', 'teamwork', 'problem solving', 'project management'],
            'language': ['english', 'french', 'spanish', 'german', 'chinese', 'italian'],
        }
        
        # Termes techniques
        self.technical_terms = [
            # Langages
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
            'Swift', 'Kotlin', 'Scala', 'HTML', 'CSS', 'SQL', 'NoSQL', 'GraphQL', 'R', 'MATLAB',
            'Shell', 'Bash', 'PowerShell',
            
            # Frameworks
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'FastAPI', 'Spring', 'Laravel',
            'Symfony', 'Express', '.NET', 'ASP.NET', 'React Native', 'Flutter',
            
            # Bases de données
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server', 'SQLite', 'MariaDB',
            'Cassandra', 'Neo4j', 'Elasticsearch', 'Firebase',
            
            # Outils/Cloud
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'Jenkins', 'GitLab', 'GitHub',
            'JIRA', 'Confluence', 'Trello', 'Ansible', 'Terraform', 'Prometheus', 'Grafana',
            'Splunk', 'Kibana',
            
            # Data/AI
            'Machine Learning', 'Deep Learning', 'Data Science', 'Data Analysis', 'Big Data',
            'AI', 'Artificial Intelligence', 'NLP', 'Natural Language Processing',
            'Computer Vision', 'Pandas', 'NumPy', 'TensorFlow', 'PyTorch', 'Scikit-learn',
            'Tableau', 'Power BI', 'Excel',
            
            # Méthodologies
            'Agile', 'Scrum', 'Kanban', 'DevOps', 'CI/CD', 'TDD', 'BDD', 'Waterfall',
            
            # Autres
            'REST', 'API', 'Microservices', 'MVC', 'OOP', 'Functional Programming', 'Linux',
            'Windows', 'macOS', 'iOS', 'Android',
        ]
    
    def extract_all(self, cv_text: str) -> Dict[str, Any]:
        """Extraction complète depuis n'importe quel CV"""
        
        try:
            # Nettoyer le texte
            cv_text = self.clean_text(cv_text)
            
            logger.info(f"🔍 Extraction démarrée, texte de {len(cv_text)} caractères")
            
            result = {
                'personal': self.extract_personal_info(cv_text),
                'skills': self.extract_skills_universal(cv_text),
                'experience': self.extract_experience_universal(cv_text),
                'education': self.extract_education_universal(cv_text),
                'projects': self.extract_projects_universal(cv_text),
                'languages': self.extract_languages_universal(cv_text),
                'summary': self.analyze_structure(cv_text),
                'metadata': {
                    'extraction_date': datetime.now().isoformat(),
                    'text_length': len(cv_text),
                    'word_count': len(cv_text.split())
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur dans extract_all: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Retourner une structure vide en cas d'erreur
            return {
                'personal': {'fullname': None, 'email': None, 'phone': None},
                'skills': [],
                'experience': [],
                'education': [],
                'projects': [],
                'languages': [],
                'summary': {'structure_score': 0, 'sections_present': []},
                'metadata': {'extraction_date': datetime.now().isoformat(), 'error': str(e)}
            }
    
    def clean_text(self, text: str) -> str:
        """Nettoyer le texte"""
        if not text:
            return ""
        
        # Remplacer les retours à la ligne
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Remplacer les tabulations par des espaces
        text = re.sub(r'\t', ' ', text)
        
        # Remplacer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Garder les sauts de ligne pour la structure
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def extract_personal_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extraire les informations personnelles - OPTIMISÉ"""
        info = {
            'fullname': None,
            'email': None,
            'phone': None,
            'address': None,
            'linkedin': None,
            'github': None,
        }
        
        try:
            # Extraire email
            email_match = re.search(self.patterns['email'][0], text)
            if email_match:
                info['email'] = email_match.group(0).strip()
                logger.info(f"   📧 Email trouvé: {info['email']}")
            
            # Extraire téléphone
            for pattern in self.patterns['phone']:
                phone_match = re.search(pattern, text)
                if phone_match:
                    phone = phone_match.group(0)
                    phone_clean = re.sub(r'[^\d+]', '', phone)
                    if len(phone_clean) >= 10:
                        info['phone'] = phone_clean
                        logger.info(f"   📞 Téléphone trouvé: {info['phone']}")
                        break
            
            # 🔥 EXTRACTION DU NOM - MULTIPLES STRATÉGIES
            lines = text.split('\n')
            
            # Stratégie 1: Chercher ligne avec nom en majuscules (style malgache)
            for line in lines[:15]:
                line = line.strip()
                if 4 <= len(line) <= 100:
                    # Pattern pour "RANDRIANIRINIMARO Manaosoa Fanantenana Jean Claude"
                    pattern_malgache = r'^([A-ZÀ-Ÿ]{3,})\s+([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)$'
                    match = re.match(pattern_malgache, line)
                    if match:
                        info['fullname'] = line
                        logger.info(f"   👤 Nom trouvé (style malgache): {line}")
                        break
            
            # Stratégie 2: Chercher après "Curriculum Vitae" ou "CV"
            if not info['fullname']:
                for i, line in enumerate(lines[:20]):
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ['curriculum', 'vitae', 'cv', 'resume']):
                        # Chercher dans les 3 lignes suivantes
                        for j in range(1, 4):
                            if i + j < len(lines):
                                candidate = lines[i + j].strip()
                                if 4 <= len(candidate) <= 80 and not self.is_false_positive(candidate):
                                    info['fullname'] = candidate
                                    logger.info(f"   👤 Nom trouvé (après CV): {candidate}")
                                    break
                        if info['fullname']:
                            break
            
            # Stratégie 3: Chercher la première ligne significative
            if not info['fullname']:
                for line in lines[:10]:
                    line = line.strip()
                    if 4 <= len(line) <= 80:
                        # Vérifier que ça ressemble à un nom (pas d'email, pas de téléphone)
                        if not ('@' in line or re.search(r'\d{10,}', line.replace(' ', ''))):
                            words = line.split()
                            if len(words) >= 2:
                                # Vérifier que le premier mot commence par une majuscule
                                if words[0] and words[0][0].isupper():
                                    info['fullname'] = line
                                    logger.info(f"   👤 Nom trouvé (ligne significative): {line}")
                                    break
            
            # LinkedIn et GitHub
            linkedin_match = re.search(r'linkedin\.com/in/([a-zA-Z0-9\-]+)', text, re.IGNORECASE)
            if linkedin_match:
                info['linkedin'] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
                logger.info(f"   🔗 LinkedIn trouvé")
            
            github_match = re.search(r'github\.com/([a-zA-Z0-9\-]+)', text, re.IGNORECASE)
            if github_match:
                info['github'] = f"https://github.com/{github_match.group(1)}"
                logger.info(f"   💻 GitHub trouvé")
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction info personnelles: {e}")
        
        return info
    
    def is_false_positive(self, text: str) -> bool:
        """Détecter les faux positifs pour les noms"""
        if not text:
            return True
        
        text_lower = text.lower()
        
        # Mots à exclure
        exclude_words = [
            'cv', 'curriculum', 'vitae', 'resume', 'candidature',
            'coordonnées', 'contact', 'information', 'informations',
            'profile', 'profil', 'summary', 'objectif', 'objective',
            'telephone', 'téléphone', 'email', 'mail', 'adresse',
            'competences', 'compétences', 'skills', 'experience',
            'expérience', 'education', 'formation', 'projects',
            'projets', 'languages', 'langues', 'hobbies', 'centre',
            'intérêt', 'intérêts'
        ]
        
        # Vérifier si le texte contient un mot exclu
        if any(exclude in text_lower for exclude in exclude_words):
            return True
        
        # Vérifier si c'est une date
        if re.search(r'\b(19|20)\d{2}\b', text):
            return True
        
        # Vérifier si c'est un email
        if '@' in text:
            return True
        
        # Vérifier si c'est un numéro de téléphone
        if re.search(r'\d{10,}', text.replace(' ', '')):
            return True
        
        return False
    
    def extract_skills_universal(self, text: str) -> List[Dict]:
        """Extraire les compétences"""
        skills = []
        found_terms = set()
        
        try:
            # Stratégie 1: Chercher la section compétences
            skill_section_patterns = [
                r'(?:COMP[ÉE]TENCES|SKILLS|TECHNICAL SKILLS)[:\s]*\n([\s\S]*?)(?=\n\s*\n[A-Z]|\Z)',
                r'(?:EXPERTISE|COMPETENCIES)[:\s]*\n([\s\S]*?)(?=\n\s*\n[A-Z]|\Z)',
            ]
            
            for pattern in skill_section_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    skill_text = match.group(1)
                    # Extraire les lignes
                    lines = skill_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            # Chercher les termes techniques dans la ligne
                            for term in self.technical_terms:
                                if term.lower() in line.lower() and term not in found_terms:
                                    skills.append({
                                        'name': term,
                                        'category': self.categorize_skill(term)
                                    })
                                    found_terms.add(term)
                    break
            
            # Stratégie 2: Chercher dans tout le texte
            if len(skills) < 5:
                for term in self.technical_terms:
                    if term.lower() in text.lower() and term not in found_terms:
                        skills.append({
                            'name': term,
                            'category': self.categorize_skill(term)
                        })
                        found_terms.add(term)
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction compétences: {e}")
        
        return skills[:20]
    
    def categorize_skill(self, skill: str) -> str:
        """Catégoriser une compétence"""
        skill_lower = skill.lower()
        
        for category, keywords in self.skill_categories.items():
            for keyword in keywords:
                if keyword in skill_lower:
                    return category
        
        return 'other'
    
    def extract_experience_universal(self, text: str) -> List[Dict]:
        """Extraire l'expérience professionnelle"""
        experiences = []
        
        try:
            # Chercher section expérience
            exp_patterns = [
                r'(?:EXP[ÉE]RIENCE|EXPERIENCE|WORK EXPERIENCE)[:\s]*\n([\s\S]*?)(?=\n\s*\n(?:FORMATION|EDUCATION|COMP[ÉE]TENCES|SKILLS|PROJETS)|\Z)',
                r'(?:EMPLOI|EMPLOYMENT|CAREER)[:\s]*\n([\s\S]*?)(?=\n\s*\n(?:FORMATION|EDUCATION)|\Z)',
            ]
            
            for pattern in exp_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    exp_text = match.group(1)
                    # Séparer par les lignes vides
                    blocks = re.split(r'\n\s*\n', exp_text)
                    
                    for block in blocks[:5]:
                        block = block.strip()
                        if block:
                            exp = self.parse_experience_block(block)
                            if exp:
                                experiences.append(exp)
                    break
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction expérience: {e}")
        
        return experiences
    
    def parse_experience_block(self, block: str) -> Optional[Dict]:
        """Parser un bloc d'expérience"""
        try:
            lines = block.split('\n')
            if not lines:
                return None
            
            exp = {
                'poste': '',
                'entreprise': '',
                'debut': '',
                'fin': '',
                'description': []
            }
            
            # Chercher les dates dans la première ligne
            first_line = lines[0]
            date_match = re.search(r'(\d{4})\s*[-–]\s*(\d{4}|aujourd\'hui|present|now|actuel)', first_line, re.IGNORECASE)
            
            if date_match:
                exp['debut'] = date_match.group(1)
                exp['fin'] = date_match.group(2)
                # Enlever les dates pour avoir le poste/entreprise
                first_line = re.sub(r'\d{4}\s*[-–]\s*(?:\d{4}|aujourd\'hui|present|now)', '', first_line).strip()
            
            # Chercher "chez" ou "at" pour séparer poste et entreprise
            chez_match = re.search(r'(.+?)\s+(?:chez|at|@)\s+(.+)', first_line, re.IGNORECASE)
            if chez_match:
                exp['poste'] = chez_match.group(1).strip()
                exp['entreprise'] = chez_match.group(2).strip()
            else:
                exp['poste'] = first_line
            
            # Extraire la description des lignes suivantes
            for line in lines[1:]:
                line = line.strip()
                if line:
                    exp['description'].append(line)
            
            return exp
            
        except Exception as e:
            logger.error(f"❌ Erreur parsing bloc expérience: {e}")
            return None
    
    def extract_education_universal(self, text: str) -> List[Dict]:
        """Extraire la formation"""
        education = []
        
        try:
            # Chercher section formation
            edu_patterns = [
                r'(?:FORMATION|EDUCATION|ACADEMIC)[:\s]*\n([\s\S]*?)(?=\n\s*\n(?:COMP[ÉE]TENCES|SKILLS|EXP[ÉE]RIENCE|PROJETS)|\Z)',
                r'(?:DIPL[ÔO]MES|DEGREES|STUDIES)[:\s]*\n([\s\S]*?)(?=\n\s*\n(?:COMP[ÉE]TENCES|SKILLS)|\Z)',
            ]
            
            for pattern in edu_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    edu_text = match.group(1)
                    lines = edu_text.split('\n')
                    
                    current_edu = {}
                    for line in lines:
                        line = line.strip()
                        if line:
                            # Chercher année
                            year_match = re.search(r'\b(19|20)\d{2}\b', line)
                            if year_match:
                                current_edu['annee'] = year_match.group(0)
                            
                            # Chercher diplôme
                            diplome_keywords = ['master', 'licence', 'bachelor', 'phd', 'doctorat', 'ingénieur', 'bts', 'dut']
                            for keyword in diplome_keywords:
                                if keyword in line.lower():
                                    current_edu['diplome'] = line
                                    break
                            
                            # Chercher établissement
                            if 'université' in line.lower() or 'école' in line.lower() or 'school' in line.lower() or 'institut' in line.lower():
                                current_edu['etablissement'] = line
                            
                            # Si on a assez d'info, sauvegarder
                            if current_edu and (current_edu.get('diplome') or current_edu.get('etablissement')):
                                education.append(current_edu.copy())
                                current_edu = {}
                    
                    break
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction formation: {e}")
        
        return education[:3]
    
    def extract_projects_universal(self, text: str) -> List[Dict]:
        """Extraire les projets"""
        projects = []
        
        try:
            # Chercher section projets
            proj_patterns = [
                r'(?:PROJETS|PROJECTS|R[ÉE]ALISATIONS)[:\s]*\n([\s\S]*?)(?=\n\s*\n(?:COMP[ÉE]TENCES|SKILLS|LANGUES|LANGUAGES)|\Z)',
                r'(?:ACHIEVEMENTS|PORTFOLIO)[:\s]*\n([\s\S]*?)(?=\n\s*\n(?:LANGUES|LANGUAGES)|\Z)',
            ]
            
            for pattern in proj_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    proj_text = match.group(1)
                    blocks = re.split(r'\n\s*\n', proj_text)
                    
                    for block in blocks[:3]:
                        block = block.strip()
                        if block:
                            lines = block.split('\n')
                            if lines:
                                project = {
                                    'titre': lines[0].strip(),
                                    'description': ' '.join(lines[1:])[:200],
                                    'technologies': [],
                                    'periode': ''
                                }
                                projects.append(project)
                    break
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction projets: {e}")
        
        return projects
    
    def extract_languages_universal(self, text: str) -> List[Dict]:
        """Extraire les langues"""
        languages = []
        
        try:
            # Chercher section langues
            lang_patterns = [
                r'(?:LANGUES|LANGUAGES|LANGUE)[:\s]*\n([\s\S]*?)(?=\n\s*\n(?:CENTRE D\'INT[ÉE]R[ÊE]T|INTERETS|HOBBIES)|\Z)',
                r'(?:IDIOMES)[:\s]*\n([\s\S]*?)(?=\n\s*\n[A-Z]|\Z)',
            ]
            
            for pattern in lang_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    lang_text = match.group(1)
                    lines = lang_text.split('\n')
                    
                    common_langs = {
                        'français': ['courant', 'natif', 'bilingue', 'maternelle'],
                        'anglais': ['courant', 'fluent', 'intermédiaire', 'débutant', 'toeic', 'ielts'],
                        'espagnol': ['courant', 'intermédiaire', 'débutant'],
                        'allemand': ['courant', 'intermédiaire', 'débutant'],
                        'chinois': ['courant', 'intermédiaire', 'débutant'],
                        'italien': ['courant', 'intermédiaire', 'débutant'],
                    }
                    
                    for line in lines:
                        line_lower = line.lower()
                        for lang, levels in common_langs.items():
                            if lang in line_lower:
                                niveau = 'intermédiaire'
                                for level in levels:
                                    if level in line_lower:
                                        niveau = level
                                        break
                                
                                languages.append({
                                    'langue': lang.capitalize(),
                                    'niveau': niveau.capitalize()
                                })
                                break
                    
                    break
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction langues: {e}")
        
        return languages
    
    def analyze_structure(self, text: str) -> Dict:
        """Analyser la structure du CV"""
        sections_found = []
        
        try:
            common_sections = [
                ('experience', r'EXP[ÉE]RIENCE|EXPERIENCE|WORK'),
                ('education', r'FORMATION|EDUCATION|DIPL[ÔO]MES'),
                ('skills', r'COMP[ÉE]TENCES|SKILLS|TECHNICAL'),
                ('projects', r'PROJETS|PROJECTS|R[ÉE]ALISATIONS'),
                ('languages', r'LANGUES|LANGUAGES'),
                ('summary', r'SUMMARY|PROFIL|OBJECTIVE'),
                ('contact', r'CONTACT|COORDONN[ÉE]ES'),
            ]
            
            for section_name, pattern in common_sections:
                if re.search(pattern, text, re.IGNORECASE):
                    sections_found.append(section_name)
            
            # Calculer score de structure
            structure_score = (len(sections_found) / len(common_sections)) * 100
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse structure: {e}")
            structure_score = 0
        
        return {
            'sections_present': sections_found,
            'structure_score': round(structure_score, 1),
            'word_count': len(text.split()),
            'char_count': len(text),
        }

# Instance globale
cv_extractor = CVExtractor()

def extract_info(cv_text: str) -> Dict:
    """Fonction principale d'extraction"""
    try:
        logger.info(f"🔍 Début extraction NLP...")
        
        result = cv_extractor.extract_all(cv_text)
        
        # Formater pour compatibilité
        formatted = {
            'fullname': result['personal'].get('fullname'),
            'email': result['personal'].get('email'),
            'phone': result['personal'].get('phone'),
            'skills': [s['name'] for s in result['skills']][:10],
            'experience': result['experience'],
            'education': result['education'],
            'projects': result['projects'],
            'languages': result['languages'],
            'summary': result['summary'],
            'raw_data': result
        }
        
        # Logging détaillé
        logger.info(f"✅ Extraction NLP réussie")
        if formatted['fullname']:
            logger.info(f"   👤 Nom extrait: {formatted['fullname']}")
        if formatted['email']:
            logger.info(f"   📧 Email extrait: {formatted['email']}")
        if formatted['phone']:
            logger.info(f"   📞 Téléphone extrait: {formatted['phone']}")
        if formatted['skills']:
            logger.info(f"   🔧 {len(formatted['skills'])} compétences extraites")
        logger.info(f"   📊 Score structure: {result['summary']['structure_score']}")
        
        return formatted
        
    except Exception as e:
        logger.error(f"❌ Erreur extraction: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Retourner une structure vide en cas d'erreur
        return {
            'fullname': None,
            'email': None,
            'phone': None,
            'skills': [],
            'experience': [],
            'education': [],
            'projects': [],
            'languages': [],
            'summary': {'structure_score': 0, 'sections_present': []},
            'raw_data': {}
        }