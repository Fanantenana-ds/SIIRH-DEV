import os
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base



# --- Configuration base de données (env vars possible) ---
DB_USER = os.getenv("DB_USER", "siirh_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "manaosoa09")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "siirh_db")
Base = declarative_base()

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- SQLAlchemy setup ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Optional: define ORM models here if you want create_all to work.
# Example (uncomment and adapt only if you use ORM models in this file):
#
# from sqlalchemy import Column, Integer, String, Boolean
# class Utilisateur(Base):
#     __tablename__ = "utilisateurs"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, nullable=False)
#     email = Column(String, nullable=False, unique=True)
#     password = Column(String, nullable=False)
#     role = Column(String)
#     actif = Column(Boolean, default=True)

def get_db():
    """
    Dependency for FastAPI - yields a DB session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Passlib/bcrypt handling (safe fallback included) ---
try:
    # passlib with bcrypt backend
    from passlib.hash import bcrypt
    _HAS_PASSLIB = True
except Exception:
    _HAS_PASSLIB = False
    print("⚠️ passlib/bcrypt tsy hita: ny mot de passe dia tsy ho hashé (fallback plaintext)."
          " Ho an'ny sécurité, apetraho ny passlib sy bcrypt amin'ny venv-nao.")


def _truncate_for_bcrypt(password: str) -> str:
    """
    Bcrypt supports max 72 bytes. Truncate UTF-8 bytes to 72 then decode safely.
    """
    if password is None:
        return ""
    b = password.encode("utf-8")[:72]
    return b.decode("utf-8", errors="ignore")


def hash_password(password: str) -> str:
    """
    Returns hashed password if passlib available; otherwise returns plaintext fallback.
    """
    if password is None:
        return ""
    safe_pw = _truncate_for_bcrypt(password)
    if _HAS_PASSLIB:
        try:
            return bcrypt.hash(safe_pw)
        except Exception as e:
            print("⚠️ Olana tamin'ny bcrypt hashing:", e)
            print("   — Hampiasa fallback plaintext (tsy soso-kevitra ho production).")
            return safe_pw
    # fallback
    return safe_pw


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Helper to verify password; used only if wanted programmatically.
    """
    if not hashed_password:
        return False
    if _HAS_PASSLIB:
        try:
            # Note: truncate plain_password same way before verify (consistent with hashing).
            return bcrypt.verify(_truncate_for_bcrypt(plain_password), hashed_password)
        except Exception:
            return False
    # fallback: direct compare (only for dev)
    return _truncate_for_bcrypt(plain_password) == hashed_password


# --- Admin auto-create / seed logic (uses raw SQL to avoid model coupling) ---
def create_default_admin(force: bool = False):
    """
    Create or update a default admin in 'utilisateurs' table.
    - Reads ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_USERNAME, ADMIN_ROLE, ADMIN_ACTIF from env.
    - If force=True, update existing account (match by email).
    """
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@rh.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_ROLE = os.getenv("ADMIN_ROLE", "admin")
    ADMIN_ACTIF = os.getenv("ADMIN_ACTIF", "true").lower() in ("1", "true", "yes", "y")

    password_to_store = hash_password(ADMIN_PASSWORD)

    check_sql = text("SELECT id FROM utilisateurs WHERE email = :email OR username = :username LIMIT 1")
    insert_sql = text("""
        INSERT INTO utilisateurs (username, email, role, actif, password)
        VALUES (:username, :email, :role, :actif, :password)
        RETURNING id
    """)
    update_sql = text("""
        UPDATE utilisateurs
        SET username = :username, role = :role, actif = :actif, password = :password
        WHERE email = :email
        RETURNING id
    """)

    try:
        with engine.begin() as conn:
            res = conn.execute(check_sql, {"email": ADMIN_EMAIL, "username": ADMIN_USERNAME}).fetchone()
            if res and not force:
                print(f"⚙️  Admin '{ADMIN_EMAIL}' efa misy (id={res[0]}). Raha te hanavao: create_default_admin(force=True).")
                return {"created": False, "reason": "exists", "id": res[0]}
            if res and force:
                updated = conn.execute(update_sql, {
                    "username": ADMIN_USERNAME,
                    "role": ADMIN_ROLE,
                    "actif": ADMIN_ACTIF,
                    "password": password_to_store,
                    "email": ADMIN_EMAIL
                }).fetchone()
                print(f"🔁 Admin '{ADMIN_EMAIL}' nohavaozina (id={updated[0] if updated else 'unknown'}).")
                return {"created": False, "updated": True, "id": updated[0] if updated else None}
            new = conn.execute(insert_sql, {
                "username": ADMIN_USERNAME,
                "email": ADMIN_EMAIL,
                "role": ADMIN_ROLE,
                "actif": ADMIN_ACTIF,
                "password": password_to_store
            }).fetchone()
            print(f"✅ Admin '{ADMIN_EMAIL}' voaforona soa aman-tsara (id={new[0] if new else 'unknown'}).")
            return {"created": True, "id": new[0] if new else None}
    except SQLAlchemyError as e:
        print("❌ Erreur lors de la création de l'admin:", e)
        return {"created": False, "error": str(e)}


def create_tables_if_requested():
    """
    Optional: creates tables from ORM models defined in this module (if any).
    Use for development only.
    """
    create_flag = os.getenv("CREATE_TABLES", "false").lower() in ("1", "true", "yes", "y")
    return create_flag


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DB helper: create default admin and optionally create tables.")
    parser.add_argument("--force", action="store_true", help="Force update the admin if it exists.")
    parser.add_argument("--create-tables", action="store_true", help="Create tables from ORM models (dev only).")
    args = parser.parse_args()

    if args.create_tables or create_tables_if_requested():
        # If you have ORM models in this file or imported, this will create their tables.
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Tables created (if models defined).")
        except Exception as e:
            print("⚠️ Failed to create tables:", e)

    print("🚀 Initialisation de la base de données SIIRH...")
    res = create_default_admin(force=args.force)
    print("➡️ Result:", res)
    print("✅ Vérifie dans la table 'utilisateurs' raha tafiditra ilay admin.")
