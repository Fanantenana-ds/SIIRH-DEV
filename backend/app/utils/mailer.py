# # app/utils/mailer.py
# import smtplib
# from email.message import EmailMessage
# import mimetypes
# import os
# from dotenv import load_dotenv

# # Charger variables .env
# load_dotenv()

# SMTP_SERVER = os.getenv("SMTP_SERVER")
# SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
# SMTP_USERNAME = os.getenv("SMTP_EMAIL")
# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# def send_mail(to: str, subject: str, body: str, attachments: list = None):
#     """
#     Envoi d'email avec pièces jointes
#     - utilise config du fichier .env
#     - support PDF, images, etc.
#     """

#     if not SMTP_USERNAME or not SMTP_PASSWORD:
#         raise Exception("SMTP_EMAIL ou SMTP_PASSWORD manjavona ao amin'ny .env")

#     msg = EmailMessage()
#     msg["From"] = SMTP_USERNAME
#     msg["To"] = to
#     msg["Subject"] = subject
#     msg.set_content(body)

#     # Ajouter pièces jointes
#     if attachments:
#         for file_path in attachments:
#             if not os.path.exists(file_path):
#                 print(f"[MAILER] Fichier introuvable: {file_path}")
#                 continue

#             mime_type, _ = mimetypes.guess_type(file_path)
#             mime_main, mime_sub = mime_type.split("/")

#             with open(file_path, "rb") as f:
#                 msg.add_attachment(
#                     f.read(),
#                     maintype=mime_main,
#                     subtype=mime_sub,
#                     filename=os.path.basename(file_path)
#                 )

#     try:
#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(SMTP_USERNAME, SMTP_PASSWORD)
#             server.send_message(msg)

#         print("[MAILER] Email envoyé avec succès")

#     except Exception as e:
#         print("[MAILER] Erreur:", e)
#         raise e



# # app/utils/mailer.py - VERSION MIFANARAKA AMIN'NY ANCIEN CODE
# import smtplib
# from email.message import EmailMessage
# import mimetypes
# import os
# from dotenv import load_dotenv
# from sqlalchemy.orm import Session
# from app.models.models import SMTPConfig

# # Charger variables .env
# load_dotenv()

# def get_smtp_config(db: Session = None):
#     """
#     Récupérer la configuration SMTP:
#     1. D'abord depuis .env
#     2. Sinon depuis la base de données
#     3. Sinon erreur
#     """
#     # Essayer .env d'abord
#     SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
#     SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
#     SMTP_USERNAME = os.getenv("SMTP_EMAIL")
#     SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    
#     # Si .env configuré, utiliser ça
#     if SMTP_USERNAME and SMTP_PASSWORD:
#         print(f"[MAILER] Utilisation config .env: {SMTP_USERNAME}")
#         return {
#             "server": SMTP_SERVER,
#             "port": SMTP_PORT,
#             "username": SMTP_USERNAME,
#             "password": SMTP_PASSWORD
#         }
    
#     # Sinon, essayer la base de données
#     if db:
#         try:
#             config = db.query(SMTPConfig).first()
#             if config:
#                 print(f"[MAILER] Utilisation config DB: {config.email}")
#                 return {
#     "server": config.host,
#     "port": config.port,
#     "username": config.email,
#     "password": config.password,
#     "use_tls": config.use_tls
# }

#         except Exception as e:
#             print(f"[MAILER] Erreur accès DB: {e}")
    
#     # Aucune configuration trouvée
#     raise Exception("Configuration SMTP manquante. Configurez .env ou la base de données")

# def send_mail(to: str, subject: str, body: str, attachments: list = None, db_session: Session = None):
#     """
#     Envoi d'email avec pièces jointes
#     - essaie d'abord .env, puis base de données
#     - support PDF, images, etc.
#     """
    
#     # Récupérer la configuration
#     config = get_smtp_config(db_session)
    
#     msg = EmailMessage()
#     msg["From"] = config["username"]
#     msg["To"] = to
#     msg["Subject"] = subject
#     msg.set_content(body)

#     # Ajouter pièces jointes
#     if attachments:
#         for file_path in attachments:
#             if not os.path.exists(file_path):
#                 print(f"[MAILER] Fichier introuvable: {file_path}")
#                 continue

#             mime_type, _ = mimetypes.guess_type(file_path)
#             if not mime_type:
#                 mime_type = "application/octet-stream"
            
#             mime_main, mime_sub = mime_type.split("/") if "/" in mime_type else ("application", "octet-stream")

#             with open(file_path, "rb") as f:
#                 msg.add_attachment(
#                     f.read(),
#                     maintype=mime_main,
#                     subtype=mime_sub,
#                     filename=os.path.basename(file_path)
#                 )

#     try:
#         with smtplib.SMTP(config["server"], config["port"]) as server:
#             server.starttls()
#             server.login(config["username"], config["password"])
#             server.send_message(msg)

#         print(f"[MAILER] Email envoyé à {to}")

#     except Exception as e:
#         print("[MAILER] Erreur:", e)
#         raise Exception(f"Erreur d'envoi d'email: {str(e)}")



# # app/utils/mailer.py
# import smtplib
# from email.message import EmailMessage
# import mimetypes
# import os
# from dotenv import load_dotenv
# from sqlalchemy.orm import Session
# from app.models.models import SMTPConfig

# # Charger variables .env
# load_dotenv()


# def get_smtp_config(db: Session | None = None) -> dict:
#     """
#     Récupérer la configuration SMTP :
#     1. .env (prioritaire)
#     2. Base de données (smtp_config)
#     3. Sinon -> Exception
#     """

#     # ==============================
#     # 1️⃣ ESSAI VIA .env
#     # ==============================
#     env_username = os.getenv("SMTP_EMAIL")
#     env_password = os.getenv("SMTP_PASSWORD")

#     if env_username and env_password:
#         print(f"[MAILER] Utilisation config .env: {env_username}")
#         return {
#             "host": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
#             "port": int(os.getenv("SMTP_PORT", "587")),
#             "username": env_username,
#             "password": env_password,
#             "use_tls": True,
#         }

#     # ==============================
#     # 2️⃣ ESSAI VIA BASE DE DONNÉES
#     # ==============================
#     if db:
#         try:
#             config = db.query(SMTPConfig).first()
#             if config:
#                 print(f"[MAILER] Utilisation config DB: {config.email}")
#                 return {
#                     "host": config.host,
#                     "port": config.port or 587,
#                     "username": config.email,
#                     "password": config.password,
#                     "use_tls": config.use_tls if config.use_tls is not None else True,
#                 }
#         except Exception as e:
#             print(f"[MAILER] Erreur accès DB: {e}")

#     # ==============================
#     # 3️⃣ AUCUNE CONFIG
#     # ==============================
#     raise Exception(
#         "Configuration SMTP manquante. Configurez .env ou la base de données"
#     )


# def send_mail(
#     to: str,
#     subject: str,
#     body: str,
#     attachments: list | None = None,
#     db_session: Session | None = None,
# ):
#     """
#     Envoi d'email avec pièces jointes
#     - utilise .env si dispo
#     - sinon smtp_config (DB)
#     """

#     config = get_smtp_config(db_session)

#     msg = EmailMessage()
#     msg["From"] = config["username"]
#     msg["To"] = to
#     msg["Subject"] = subject
#     msg.set_content(body)

#     # ==============================
#     # AJOUT DES PIÈCES JOINTES
#     # ==============================
#     if attachments:
#         for file_path in attachments:
#             if not os.path.exists(file_path):
#                 print(f"[MAILER] Fichier introuvable: {file_path}")
#                 continue

#             mime_type, _ = mimetypes.guess_type(file_path)
#             if not mime_type:
#                 mime_type = "application/octet-stream"

#             maintype, subtype = (
#                 mime_type.split("/", 1)
#                 if "/" in mime_type
#                 else ("application", "octet-stream")
#             )

#             with open(file_path, "rb") as f:
#                 msg.add_attachment(
#                     f.read(),
#                     maintype=maintype,
#                     subtype=subtype,
#                     filename=os.path.basename(file_path),
#                 )

#     # ==============================
#     # ENVOI SMTP
#     # ==============================
#     try:
#         with smtplib.SMTP(config["host"], config["port"]) as server:
#             if config.get("use_tls", True):
#                 server.starttls()

#             server.login(config["username"], config["password"])
#             server.send_message(msg)

#         print(f"[MAILER] Email envoyé avec succès à {to}")

#     except Exception as e:
#         print("[MAILER] Erreur envoi email:", e)
#         raise Exception(f"Erreur d'envoi d'email: {str(e)}")





# app/utils/mailer.py - VERSION AVEC DEBUG
import smtplib
from email.message import EmailMessage
import mimetypes
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.models.models import SMTPConfig

# Charger variables .env
load_dotenv()

def get_smtp_config(db: Session | None = None) -> dict:
    """
    Récupérer la configuration SMTP avec debug
    """
    print(f"[MAILER DEBUG] get_smtp_config appelé, db={'fourni' if db else 'None'}")
    
    # ==============================
    # 1️⃣ ESSAI VIA .env
    # ==============================
    env_username = os.getenv("SMTP_EMAIL")
    env_password = os.getenv("SMTP_PASSWORD")

    if env_username and env_password:
        print(f"[MAILER] Utilisation config .env: {env_username}")
        return {
            "host": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": env_username,
            "password": env_password,
            "use_tls": True,
        }

    # ==============================
    # 2️⃣ ESSAI VIA BASE DE DONNÉES
    # ==============================
    if db:
        try:
            print("[MAILER DEBUG] Tentative de récupération depuis DB...")
            
            # Vérifier d'abord la structure de la table
            from sqlalchemy import inspect
            inspector = inspect(db.get_bind())
            columns = [col['name'] for col in inspector.get_columns('smtp_config')]
            print(f"[MAILER DEBUG] Colonnes table: {columns}")
            
            # Essayer de récupérer la config
            config = db.query(SMTPConfig).first()
            if config:
                print(f"[MAILER DEBUG] Config trouvée: {config.email}")
                print(f"[MAILER DEBUG] Host: {config.host}")
                print(f"[MAILER DEBUG] Port: {config.port}")
                print(f"[MAILER DEBUG] Password length: {len(config.password) if config.password else 0}")
                
                # Fallback pour host si null
                host = config.host if config.host else "smtp.gmail.com"
                port = config.port if config.port else 587
                
                # Vérifier si password existe
                if not config.password or config.password.strip() == "":
                    print("[MAILER DEBUG] ⚠️ Password vide ou null")
                    raise Exception("Password SMTP vide")
                
                print(f"[MAILER] Utilisation config DB: {config.email}")
                return {
                    "host": host,
                    "port": port,
                    "username": config.email,
                    "password": config.password,
                    "use_tls": config.use_tls if config.use_tls is not None else True,
                }
            else:
                print("[MAILER DEBUG] Aucune config dans la table")
                
        except Exception as e:
            print(f"[MAILER DEBUG] Erreur accès DB: {type(e).__name__}: {e}")
            # Passer à l'exception générale

    # ==============================
    # 3️⃣ AUCUNE CONFIG
    # ==============================
    raise Exception(
        "Configuration SMTP manquante. Configurez .env ou vérifiez la table smtp_config"
    )


def send_mail(
    to: str,
    subject: str,
    body: str,
    attachments: list | None = None,
    db_session: Session | None = None,
):
    """
    Envoi d'email avec fallback si échec
    """
    print(f"[MAILER] Tentative d'envoi à {to}")
    
    try:
        config = get_smtp_config(db_session)
        
        print(f"[MAILER] Configuration: {config['username']}@{config['host']}:{config['port']}")
        
        msg = EmailMessage()
        msg["From"] = config["username"]
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        # ==============================
        # AJOUT DES PIÈCES JOINTES
        # ==============================
        if attachments:
            for file_path in attachments:
                if not os.path.exists(file_path):
                    print(f"[MAILER] Fichier introuvable: {file_path}")
                    continue

                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = "application/octet-stream"

                maintype, subtype = (
                    mime_type.split("/", 1)
                    if "/" in mime_type
                    else ("application", "octet-stream")
                )

                with open(file_path, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(file_path),
                    )

        # ==============================
        # ENVOI SMTP
        # ==============================
        print(f"[MAILER] Connexion à {config['host']}:{config['port']}...")
        with smtplib.SMTP(config["host"], config["port"]) as server:
            if config.get("use_tls", True):
                server.starttls()

            server.login(config["username"], config["password"])
            server.send_message(msg)

        print(f"[MAILER] ✅ Email envoyé avec succès à {to}")
        return True

    except Exception as e:
        print(f"[MAILER] ❌ Erreur d'envoi: {type(e).__name__}: {e}")
        # Ne pas raise immédiatement, laisser le frontend récupérer le PDF
        raise Exception(f"Email non envoyé: {str(e)}")