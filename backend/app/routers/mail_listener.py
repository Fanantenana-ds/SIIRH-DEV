from fastapi import APIRouter, HTTPException, Depends
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session
from app.db import get_db, engine
from app.models.models import Candidature
from app.models.offres import Offre
from app.services.upload_service import process_cv_from_bytes
import imaplib, email, os, json, traceback, re, socket, logging
from datetime import datetime
from email.header import decode_header
import time
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from app.db import get_db, engine  
from app.routers.notifications import add_mail_notification

router = APIRouter()
MAIL_CHECK_INTERVAL = 60

# ================= LOGGING =================
logger = logging.getLogger(__name__)

# ================= CONFIGURATION SPAM =================
SPAM_DOMAINS = [
    'facebookmail.com', 'facebook.com',
    'twitter.com', 't.co',
    'linkedin.com', 'linkedinmail.com',
    'instagram.com', 'instagrammail.com',
    'mailer', 'noreply', 'no-reply',
    'notification', 'alert', 'newsletter',
    'promo', 'marketing', 'offer', 'deal',
    'discount', 'sale', 'update',
]

SPAM_KEYWORDS = [
    'facebook', 'twitter', 'linkedin', 'instagram',
    'newsletter', 'promotion', 'marketing', 'publicité',
    'sale', 'discount', 'offer', 'deal', 'soldes',
    'notification', 'alert', 'update', 'mise à jour',
    'comment', 'like', 'share', 'follow', 'suivre',
    'friend request', 'connection', 'connexion',
    'photo', 'post', 'publication',
    '💬', '👍', '👥', '📸', '🎥',
]

# ================= FONCTIONS AUXILIAIRES =================

def get_smtp_config_from_db() -> Dict[str, str]:
    """Charger configuration SMTP depuis la base de données"""
    try:
        # Créer une session DB indépendante
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        config = db.execute(text("SELECT * FROM smtp_config ORDER BY id DESC LIMIT 1")).fetchone()
        
        if config:
            logger.info(f"✅ Configuration SMTP chargée depuis DB: {config.email}")
            return {
                "email": config.email,
                "password": config.password,
                "host": getattr(config, 'host', 'smtp.gmail.com'),
                "port": getattr(config, 'port', 587),
                "use_tls": getattr(config, 'use_tls', True)
            }
        else:
            logger.warning("⚠️ Aucune configuration SMTP dans la base de données")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erreur chargement SMTP depuis DB: {str(e)}")
        return None
    finally:
        if 'db' in locals():
            db.close()

def load_smtp_config() -> Dict[str, str]:
    """Charger configuration SMTP (priorité DB, puis fallback)"""
    # 1. Essayer depuis DB
    db_config = get_smtp_config_from_db()
    
    if db_config:
        logger.info(f"📧 Utilisation config DB: {db_config['email'][:15]}...")
        return db_config
    
    # 2. Fallback: fichier JSON
    SMTP_FILE = "smtp_config.json"
    try:
        if os.path.exists(SMTP_FILE):
            with open(SMTP_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                logger.info(f"📧 Utilisation config fichier: {config.get('email')}")
                return config
    except Exception as e:
        logger.error(f"❌ Erreur chargement fichier SMTP: {e}")
    
    # 3. Fallback hardcodé (à éviter)
    logger.warning("⚠️ Utilisation configuration SMTP fallback")
    return {
        "email": "jmseraphinravelotsara@gmail.com",
        "password": "votre_app_password",
        "host": "smtp.gmail.com",
        "port": 587,
        "use_tls": True
    }

def extract_offre_ref(text: str) -> str:
    """Extraire référence d'offre"""
    if not text:
        return None
    
    text_upper = text.upper()
    
    patterns = [
        r'REF_20[0-9]{2}_[0-9]{5}',
        r'REF_OFF_20[0-9]{2}_[0-9]{4}',
        r'OFF-20[0-9]{2}-[0-9]{3}',
        r'REF[0-9]{3,}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_upper)
        if match:
            ref = match.group()
            logger.info(f"✅ Référence OFFRE trouvée: {ref}")
            return ref
    
    logger.warning(f"❌ Aucune référence OFFRE valide trouvée dans: {text_upper[:100]}")
    return None

def is_spam_email(from_email: str, subject: str, body: str) -> bool:
    """Détecter et filtrer les emails spam"""
    if not from_email:
        return True
    
    email_lower = from_email.lower()
    subject_lower = subject.lower()
    body_lower = body.lower() if body else ""
    
    # Vérifier domaines spam
    for domain in SPAM_DOMAINS:
        if domain in email_lower:
            logger.info(f"🚫 Email filtré (domaine spam): {domain}")
            return True
    
    # Vérifier mots-clés spam
    for keyword in SPAM_KEYWORDS:
        if keyword in subject_lower:
            logger.info(f"🚫 Email filtré (mot-clé spam): {keyword}")
            return True
    
    # Indicateurs réseaux sociaux
    social_indicators = [
        'a commenté', 'a aimé', 'a partagé',
        'vous suit', 'vous a suivi',
        'demande d\'ami', 'invitation à se connecter',
        'nouvelle connexion', 'nouveau follower',
        'photo tag', 'vous a tagué',
    ]
    
    for indicator in social_indicators:
        if indicator in subject_lower or indicator in body_lower:
            logger.info(f"🚫 Email filtré (réseau social): {indicator}")
            return True
    
    if 'mailer-daemon' in email_lower or 'auto' in email_lower:
        logger.info(f"🚫 Email filtré (automate)")
        return True
    
    return False

def extract_name_from_email(addr: str) -> str:
    """Extraire nom depuis adresse email"""
    try:
        if not addr or '@' not in addr:
            return "Candidat Inconnu"
        
        name_part = addr.split('@')[0]
        name_part = re.sub(r'[0-9._-]+', ' ', name_part)
        name_part = ' '.join([word.capitalize() for word in name_part.split() if word])
        
        return name_part if name_part.strip() else "Candidat"
    except:
        return "Candidat"

def split_fullname(fullname: str):
    """Diviser le nom complet en prénom et nom"""
    if not fullname:
        return "Candidat", ""
    parts = fullname.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])

def decode_email_header(header: str) -> str:
    """Décoder les en-têtes email"""
    if not header:
        return ""
    
    try:
        decoded_parts = decode_header(header)
        result_parts = []
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    if encoding:
                        result_parts.append(part.decode(encoding))
                    else:
                        try:
                            result_parts.append(part.decode('utf-8'))
                        except:
                            result_parts.append(part.decode('latin-1', errors='ignore'))
                except:
                    result_parts.append(str(part, errors='ignore'))
            else:
                result_parts.append(str(part))
        
        return ''.join(result_parts)
    except:
        return str(header) if header else ""

def is_cv_email(msg: email.message.Message) -> bool:
    """Vérifier si l'email contient un CV"""
    cv_extensions = ['.pdf', '.doc', '.docx', '.odt', '.rtf']
    cv_keywords = ['cv', 'resume', 'curriculum', 'vitae']
    
    # Vérifier pièces jointes
    for part in msg.walk():
        filename = part.get_filename()
        if filename:
            filename_lower = filename.lower()
            
            if any(filename_lower.endswith(ext) for ext in cv_extensions):
                if any(keyword in filename_lower for keyword in cv_keywords):
                    return True
                
                try:
                    content = part.get_payload(decode=True)
                    if content:
                        sample = content[:500].decode('utf-8', errors='ignore').lower()
                        if any(keyword in sample for keyword in cv_keywords):
                            return True
                except:
                    pass
    
    # Vérifier corps
    try:
        body = get_email_body(msg)
        body_lower = body.lower()
        
        strong_indicators = [
            'candidature pour',
            'postule à',
            'offre d\'emploi',
            'lettre de motivation',
            'curriculum vitae',
            'cv en pièce',
            'mon curriculum',
            'ma candidature',
            'recrutement',
        ]
        
        for indicator in strong_indicators:
            if indicator in body_lower:
                return True
        
        if extract_offre_ref(body):
            return True
        
    except:
        pass
    
    return False

def get_email_body(msg: email.message.Message) -> str:
    """Extraire le corps texte de l'email"""
    body = ""
    
    try:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
                    except:
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body += payload.decode('latin-1', errors='ignore')
                        except:
                            pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            except:
                try:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('latin-1', errors='ignore')
                except:
                    pass
    except Exception as e:
        logger.warning(f"⚠️ Erreur extraction corps email: {e}")
    
    return body

def get_email_attachments(msg: email.message.Message) -> List[tuple]:
    """Extraire les pièces jointes de type CV"""
    attachments = []
    cv_extensions = ['.pdf', '.doc', '.docx', '.odt']
    
    for part in msg.walk():
        filename = part.get_filename()
        if filename:
            filename_lower = filename.lower()
            
            if any(filename_lower.endswith(ext) for ext in cv_extensions):
                try:
                    content = part.get_payload(decode=True)
                    if content and len(content) > 1024:
                        attachments.append((filename, content))
                        logger.info(f"📎 Pièce jointe CV: {filename} ({len(content)} bytes)")
                except Exception as e:
                    logger.warning(f"⚠️ Erreur extraction pièce jointe {filename}: {e}")
    
    return attachments

# ================= FONCTION PRINCIPALE CORRIGÉE =================

is_processing = False

@router.on_event("startup")
@repeat_every(seconds=MAIL_CHECK_INTERVAL, wait_first=True)
def check_new_mails():
    """Fonction principale de vérification des nouveaux emails - VERSION CORRIGÉE"""
    global is_processing
    
    if is_processing:
        logger.info("⏳ Déjà en cours de traitement, attente...")
        return
    
    is_processing = True
    logger.info("🔍 Début vérification emails...")
    
    # Créer une session DB indépendante pour éviter les problèmes de session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Charger configuration SMTP DEPUIS DB
        smtp_config = load_smtp_config()
        email_account = smtp_config.get("email")
        email_password = smtp_config.get("password")
        
        if not email_account or not email_password:
            logger.error("❌ Configuration SMTP incomplète")
            is_processing = False
            return
        
        logger.info(f"📧 Compte utilisé: {email_account}")
        
        # 2. Connexion IMAP
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            mail.login(email_account, email_password)
            mail.select("inbox")
            logger.info("✅ Connexion IMAP réussie")
        except Exception as e:
            logger.error(f"❌ Erreur connexion IMAP: {e}")
            is_processing = False
            db.close()
            return
        
        # 3. Chercher emails non lus
        try:
            status, messages = mail.search(None, "(UNSEEN)")
            if status != "OK" or not messages[0]:
                logger.info("📭 Aucun email non lu")
                mail.logout()
                is_processing = False
                db.close()
                return
            
            email_ids = messages[0].split()
            logger.info(f"📥 {len(email_ids)} email(s) non lu(s) trouvé(s)")
        except Exception as e:
            logger.error(f"❌ Erreur recherche emails: {e}")
            mail.logout()
            is_processing = False
            db.close()
            return
        
        # 4. Charger offres disponibles
        offres = db.query(Offre).all()
        logger.info(f"📋 {len(offres)} offres disponibles en base")
        
        # 5. Obtenir le prochain ID de séquence AVANT la boucle
        try:
            sequence_query = text("SELECT nextval('candidatures_id_seq') as next_id")
            next_id_result = db.execute(sequence_query).fetchone()
            base_id = next_id_result.next_id if next_id_result else None
            logger.info(f"🔢 Prochain ID disponible: {base_id}")
        except Exception as e:
            logger.warning(f"⚠️ Impossible d'obtenir le séquence ID: {e}")
            base_id = None
        
        # 6. Traiter chaque email
        emails_traites = 0
        emails_ignores = 0
        
        for idx, email_id in enumerate(email_ids):
            email_id_str = email_id.decode('utf-8')
            current_candidate_id = base_id + idx if base_id else None
            
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"📧 TRAITEMENT EMAIL ID: {email_id_str}")
                
                # Récupérer email
                _, msg_data = mail.fetch(email_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Extraire informations
                from_header = msg.get("From", "")
                from_email = email.utils.parseaddr(from_header)[1]
                from_name_raw = email.utils.parseaddr(from_header)[0]
                from_name = decode_email_header(from_name_raw) if from_name_raw else extract_name_from_email(from_email)
                
                subject_raw = msg.get("Subject", "")
                subject = decode_email_header(subject_raw)
                
                body = get_email_body(msg)
                
                logger.info(f"👤 Expéditeur: {from_email}")
                logger.info(f"📧 Nom: {from_name}")
                logger.info(f"📝 Sujet: {subject[:100]}")
                
                # FILTRAGE SPAM
                if is_spam_email(from_email, subject, body):
                    logger.warning(f"🚫 Email SPAM - ignoré")
                    mail.store(email_id, "+FLAGS", "\\Seen")
                    emails_ignores += 1
                    continue
                
                # Vérifier CV
                if not is_cv_email(msg):
                    logger.warning(f"⏭️  Pas de CV valide - ignoré")
                    mail.store(email_id, "+FLAGS", "\\Seen")
                    emails_ignores += 1
                    continue
                
                logger.info("✅ Email avec CV validé")
                
                # RECHERCHE RÉFÉRENCE D'OFFRE
                offre_ref = extract_offre_ref(subject)
                
                if not offre_ref and body:
                    offre_ref = extract_offre_ref(body)
                    if offre_ref:
                        logger.info(f"📄 Référence dans corps: {offre_ref}")
                
                # Si pas de référence, chercher dans pièces jointes
                if not offre_ref:
                    attachments = get_email_attachments(msg)
                    for filename, _ in attachments:
                        ref = extract_offre_ref(filename)
                        if ref:
                            offre_ref = ref
                            logger.info(f"📁 Référence dans fichier: {ref}")
                            break
                
                # TROUVER L'OFFRE
                offre_trouvee = None
                if offre_ref:
                    for offre in offres:
                        if offre.job_ref == offre_ref:
                            offre_trouvee = offre
                            logger.info(f"🎯 Offre trouvée: {offre.title} (ID: {offre.id})")
                            break
                    
                    if not offre_trouvee:
                        logger.warning(f"⚠️ Référence {offre_ref} non trouvée")
                else:
                    logger.warning("⚠️ Aucune référence d'offre")
                
                # DÉCISION - Même sans référence exacte, on continue
                if not offre_ref:
                    logger.info("ℹ️ Pas de référence exacte, utilisation référence générique")
                    offre_ref = "EMAIL_" + datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # CRÉATION CANDIDATURE - VERSION CORRIGÉE AVEC INSERT DIRECT SQL
                if offre_trouvee:
                    poste = offre_trouvee.title[:100]
                    offre_id = offre_trouvee.id
                else:
                    # Offre par défaut
                    offre_defaut = offres[0] if offres else None
                    if offre_defaut:
                        poste = offre_defaut.title[:100]
                        offre_id = offre_defaut.id
                        logger.info(f"📌 Assignée à offre par défaut: {offre_defaut.job_ref}")
                    else:
                        poste = "Non spécifié"[:100]
                        offre_id = 1
                        logger.warning(f"⚠️ Aucune offre disponible, utilisation ID=1")
                       
                try:
                    now = datetime.now()
                    nom, prenom = split_fullname(from_name)
                    insert_data = {
                        "fullname": from_name[:255],
                        "nom": nom[:100],
                        "prenom": prenom[:150],
                        "email": from_email[:255],
                        "phone": None,
                        "poste": poste,
                        "offre_id": offre_id,
                        "ref_offre": offre_ref[:100],
                        "date_candidature": now,
                        "statut": "En attente",  
                        "source": "Email automatique"[:255],
                        "score": 0,
                        "score_total": 0.0,
                        "score_breakdown": json.dumps({}),
                        "cv_text": None,
                        "experience_years": 0,
                        "date_maj": now,
                        "raw_cv_s3": None,
                        "created_at": now
                    }
                    columns = ", ".join(insert_data.keys())
                    placeholders = ", ".join([f":{key}" for key in insert_data.keys()])
                    insert_query = text(f"""
                        INSERT INTO candidatures ({columns})
                        VALUES ({placeholders})
                        RETURNING id, fullname, email, statut
                    """)
                    
                    result = db.execute(insert_query, insert_data)
                    inserted_row = result.fetchone()
                    
                    if inserted_row:
                        candidature_id = inserted_row[0]
                        logger.info(f"✅ Candidature créée ID {candidature_id}")
                        logger.info(f"   👤 Nom: {inserted_row[1]}")
                        logger.info(f"   📧 Email: {inserted_row[2]}")
                        logger.info(f"   📊 Statut: {inserted_row[3]}")
                        logger.info(f"   🎯 Offre: {poste}")
                        db.commit()
                                             
                        try:
                            notification_message = f"Nouveau candidat: {from_name} ({from_email})"
                            add_mail_notification(db, notification_message)
                            logger.info(f"🔔 Notification envoyée: {notification_message}")
                        except Exception as notif_error:
                            logger.error(f"❌ Erreur envoi notification: {notif_error}")
                        attachments = get_email_attachments(msg)
                        
                        if attachments:
                            logger.info(f"📦 {len(attachments)} fichier(s) CV")
                            
                            filename, content = attachments[0]
                            
                            try:
                                logger.info(f"   ⬆️  Upload {filename}...")
                                result = process_cv_from_bytes(db, content, filename, candidature_id)
                                
                                if result and result.get("success"):
                                    logger.info(f"   ✅ Upload réussi")
                                    
                                    if result.get('nlp_info'):
                                        nlp_info = result['nlp_info']
                                        update_data = {}
                                        if nlp_info.get('fullname'):
                                            update_data['fullname'] = nlp_info['fullname'][:255]
                                            logger.info(f"   👤 Nom extrait: {nlp_info['fullname']}")
                                        
                                        if nlp_info.get('phone'):
                                            update_data['phone'] = nlp_info['phone'][:50]
                                            logger.info(f"   📞 Téléphone: {nlp_info['phone']}")
                                        
                                        if 'score' in nlp_info:
                                            update_data['score'] = nlp_info['score']
                                            update_data['score_total'] = float(nlp_info['score'])
                                            logger.info(f"   🎯 Score: {nlp_info['score']}%")
                                        if update_data:
                                            update_query = text(f"""
                                                UPDATE candidatures 
                                                SET {', '.join([f"{k} = :{k}" for k in update_data.keys()])}
                                                WHERE id = :id
                                            """)
                                            update_data['id'] = candidature_id
                                            db.execute(update_query, update_data)
                                            db.commit()
                                            logger.info(f"   ✅ Candidature mise à jour avec infos NLP")
                                    
                                else:
                                    error_msg = result.get('error', 'Erreur inconnue') if result else 'Pas de résultat'
                                    logger.warning(f"   ⚠️ Échec upload CV: {error_msg}")
                                    
                            except Exception as e:
                                logger.error(f"   ❌ Erreur traitement CV: {e}")
                        else:
                            logger.warning("⚠️ Aucun fichier CV attaché")
                    
                    else:
                        logger.error("❌ Erreur: Pas d'ID retourné après insertion")
                        continue
                        
                except Exception as e:
                    logger.error(f"❌ Erreur création candidature: {e}")
                    db.rollback()
                    mail.store(email_id, "+FLAGS", "\\Seen")
                    continue
                mail.store(email_id, "+FLAGS", "\\Seen")
                emails_traites += 1
                logger.info(f"📌 Email traité avec succès")
                
            except Exception as e:
                logger.error(f"💥 Erreur traitement email {email_id_str}: {e}")
                logger.error(traceback.format_exc())
                continue
        mail.logout()
        
        logger.info(f"\n{'='*60}")
        logger.info("🎯 SYNTHÈSE")
        logger.info(f"   📥 Total emails: {len(email_ids)}")
        logger.info(f"   ✅ Traités: {emails_traites}")
        logger.info(f"   🚫 Ignorés: {emails_ignores}")
        
    except Exception as e:
        logger.error(f"💥 Erreur générale check_new_mails: {e}")
        logger.error(traceback.format_exc())
    finally:
        is_processing = False
        if 'db' in locals():
            db.close()
        logger.info("🔚 Fin traitement emails")

# ================= ROUTES API =================

@router.get("/test-connection")
async def test_smtp_connection():
    """Tester la connexion SMTP/IMAP"""
    try:
        smtp_config = load_smtp_config()
        
        if not smtp_config.get("email") or not smtp_config.get("password"):
            return {"status": "error", "message": "Configuration SMTP manquante"}
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(smtp_config["email"], smtp_config["password"])
        
        mail.select("inbox")
        status, messages = mail.search(None, "ALL")
        total_emails = len(messages[0].split()) if messages[0] else 0
        
        mail.logout()
        
        return {
            "status": "success",
            "message": "Connexion IMAP réussie",
            "email_account": smtp_config["email"],
            "total_emails": total_emails,
            "source": "Base de données" if get_smtp_config_from_db() else "Fallback"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/check-offres")
async def check_available_offres(db: Session = Depends(get_db)):
    """Vérifier les offres disponibles"""
    offres = db.query(Offre).all()
    
    result = []
    for offre in offres:
        result.append({
            "id": offre.id,
            "job_ref": offre.job_ref,
            "title": offre.title,
            "has_scoring": bool(offre.w_exp or offre.w_skills)
        })
    
    return {
        "total_offres": len(offres),
        "offres": result
    }

@router.post("/force-check")
async def force_email_check():
    """Forcer une vérification manuelle"""
    check_new_mails()
    return {"message": "Vérification déclenchée"}

@router.get("/current-smtp")
async def get_current_smtp_config():
    """Obtenir la configuration SMTP actuelle"""
    smtp_config = load_smtp_config()
    
    if not smtp_config:
        return {"status": "error", "message": "Aucune configuration"}
    
    return {
        "status": "success",
        "email": smtp_config.get("email", ""),
        "host": smtp_config.get("host", ""),
        "port": smtp_config.get("port", ""),
        "source": "DB" if get_smtp_config_from_db() else "Fallback"
    }

@router.get("/smtp-from-db")
async def get_smtp_from_db():
    """Obtenir la configuration SMTP directement depuis DB"""
    config = get_smtp_config_from_db()
    
    if config:
        return {
            "status": "success",
            "email": config["email"],
            "has_password": bool(config["password"]),
            "host": config["host"],
            "port": config["port"]
        }
    else:
        return {"status": "error", "message": "Aucune config SMTP en DB"}