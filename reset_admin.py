#!/usr/bin/env python3
"""
reset_admin.py
Script simple pour mettre à jour (ou créer) un compte admin dans la base SIIRH.

Usage:
  (activate your venv if needed)
  python3 reset_admin.py

Paramètres modifiables en haut du fichier.
"""

import os
from getpass import getpass

# --- Config: change these values if needed ---
ADMIN_EMAIL_DEFAULT = os.getenv("ADMIN_EMAIL", "admin@rh.local")
ADMIN_USERNAME_DEFAULT = os.getenv("ADMIN_USERNAME", "admin")
# Si vous voulez saisir le mot de passe de façon interactive, laissez ADMIN_PASSWORD_DEFAULT vide
ADMIN_PASSWORD_DEFAULT = os.getenv("ADMIN_PASSWORD", "")

# --- Import DB & models (do not change) ---
# Le script suppose la structure app/ avec app/db.py et app/models/... déjà en place.
try:
    from app.db import SessionLocal
    # import model class (adapté si vous avez app/models/__init__.py qui expose Utilisateur)
    try:
        from app.models.models import Utilisateur
    except Exception:
        # fallback if models exposed differently
        from app.models import Utilisateur
except Exception as e:
    print("Erreur d'importation : assurez-vous d'être dans le dossier backend et que le venv est activé.")
    print("Détail:", e)
    raise SystemExit(1)


# --- Hash password helper (essaie passlib -> bcrypt puis fallback plaintext) ---
def hash_password_raw(password: str) -> str:
    """
    Tente d'utiliser passlib CryptContext avec bcrypt.
    Si passlib/bcrypt non disponible, renvoie le mot de passe en clair (avec avertissement).
    """
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    except Exception as e:
        print("⚠️  passlib/bcrypt non disponible ou erreur lors du hashage.")
        print("⚠️  Le mot de passe sera stocké en clair (recommandez d'installer passlib[bcrypt]).")
        return password


def prompt_for_password(default: str = "") -> str:
    if default:
        # si on a un default via env, on propose de l'utiliser
        use_default = input(f"Utiliser le mot de passe par défaut défini (oui/non) ? [oui]: ").strip().lower()
        if use_default in ("", "o", "oui", "y", "yes"):
            return default
    # sinon demander en input masqué
    while True:
        p = getpass("Nouveau mot de passe admin (sera masqué) : ")
        if not p:
            print("Mot de passe vide — veuillez en saisir un.")
            continue
        p2 = getpass("Confirmer le mot de passe : ")
        if p != p2:
            print("Les mots de passe ne correspondent pas — essayez encore.")
            continue
        return p


def main():
    # lire / proposer valeurs
    email = input(f"Email admin [{ADMIN_EMAIL_DEFAULT}]: ").strip() or ADMIN_EMAIL_DEFAULT
    username = input(f"Username [{ADMIN_USERNAME_DEFAULT}]: ").strip() or ADMIN_USERNAME_DEFAULT

    password = ADMIN_PASSWORD_DEFAULT
    if not password:
        password = prompt_for_password(ADMIN_PASSWORD_DEFAULT)
    else:
        print("Mot de passe pris depuis variable d'environnement.")

    # hash
    hashed = hash_password_raw(password)

    db = SessionLocal()
    try:
        user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
        if user:
            user.username = username or user.username
            user.password = hashed
            user.actif = True
            # si le model a 'role', on peut forcer 'admin' ou 'rh'
            if hasattr(user, "role"):
                user.role = getattr(user, "role", "admin") or "admin"
            db.add(user)
            db.commit()
            print(f"✅ Utilisateur existant mis à jour : {email}")
        else:
            # création
            kwargs = {
                "username": username,
                "email": email,
                "password": hashed,
            }
            # role / actif si présents dans le modèle
            try:
                from sqlalchemy import inspect
                cols = [c.key for c in inspect(Utilisateur).mapper.column_attrs]
                if "role" in cols:
                    kwargs["role"] = "admin"
                if "actif" in cols:
                    kwargs["actif"] = True
            except Exception:
                pass

            new_user = Utilisateur(**kwargs)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"✅ Nouvel admin créé : {email}")

        print("➡️  Vous pouvez maintenant vous connecter via le front (frontend_rh).")
        print(f"   Email : {email}")
        print(f"   Mot de passe : (celui que vous avez saisi ou défini en env)")
    finally:
        db.close()


if __name__ == "__main__":
    main()

