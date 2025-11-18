# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from passlib.context import CryptContext
# from jose import jwt
# from datetime import datetime, timedelta
# from pydantic import BaseModel, EmailStr
# from app.db import get_db
# from app.models import Utilisateur
# import random, string

# router = APIRouter(tags=["Authentification"])

# # --- CONFIG JWT ---
# SECRET_KEY = "secretkeyfortoken123"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60

# # --- PASSWORD HASHER ---
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # --- MODELS Pydantic ---
# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# class ForgotPasswordRequest(BaseModel):
#     email: EmailStr

# class ResetPasswordRequest(BaseModel):
#     token: str
#     new_password: str

# # --- UTILITAIRES ---
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# def generate_reset_token(length=6):
#     return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


# # --- REGISTER ---
# @router.post("/register")
# def register_user(user: LoginRequest, db: Session = Depends(get_db)):
#     existing_user = db.query(Utilisateur).filter(Utilisateur.email == user.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email déjà utilisé")

#     hashed_password = get_password_hash(user.password)
#     new_user = Utilisateur(
#         username=user.email.split("@")[0],
#         email=user.email,
#         password=hashed_password,
#         role="admin",
#         actif=True
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return {"message": "Utilisateur créé avec succès", "email": new_user.email}


# # --- LOGIN RH ---
# @router.post("/login_rh")
# def login_rh(request: LoginRequest, db: Session = Depends(get_db)):
#     user = db.query(Utilisateur).filter(Utilisateur.email == request.email).first()
#     if not user or not verify_password(request.password, user.password):
#         raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

#     access_token = create_access_token(data={"sub": user.email, "role": user.role})
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": {
#             "email": user.email,
#             "username": user.username,
#             "role": user.role
#         }
#     }

# # --- FORGOT PASSWORD ---
# reset_tokens = {}  # stock temporaire {email: token}

# @router.post("/forgot_password")
# def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
#     user = db.query(Utilisateur).filter(Utilisateur.email == request.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Email introuvable")

#     token = generate_reset_token()
#     reset_tokens[request.email] = token

#     # Ici normalement envoyer email avec le token
#     print(f"[DEBUG] Reset token pour {request.email}: {token}")

#     return {"message": "Un code de réinitialisation a été envoyé à votre email"}

# # --- RESET PASSWORD ---
# @router.post("/reset_password")
# def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
#     # Vérifier si le token existe
#     email = None
#     for k, v in reset_tokens.items():
#         if v == request.token:
#             email = k
#             break
#     if not email:
#         raise HTTPException(status_code=400, detail="Token invalide")

#     user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Utilisateur introuvable")

#     user.password = get_password_hash(request.new_password)
#     db.commit()
#     del reset_tokens[email]

#     return {"message": "Mot de passe modifié avec succès"}









from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from app.db import get_db
from app.models.models import Utilisateur
import random, string

router = APIRouter(tags=["Authentification"])

# --- CONFIG JWT ---
SECRET_KEY = "secretkeyfortoken123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- PASSWORD HASHER ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- MODELS Pydantic ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# --- UTILITAIRES ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generate_reset_token(length=6):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


# --- REGISTER (🔒 corrigé: tsy login automatique intsony) ---
@router.post("/register")
def register_user(user: LoginRequest, db: Session = Depends(get_db)):
    existing_user = db.query(Utilisateur).filter(Utilisateur.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    hashed_password = get_password_hash(user.password)
    new_user = Utilisateur(
        username=user.email.split("@")[0],
        email=user.email,
        password=hashed_password,
        role="user",   # 👉 pas "admin" par défaut
        actif=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 👇 On ne retourne plus de token (sécurité)
    return {"message": "Utilisateur créé avec succès. Veuillez vous connecter pour continuer."}


# --- LOGIN RH ---
@router.post("/login_rh")
def login_rh(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == request.email).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
    }


# --- FORGOT PASSWORD ---
reset_tokens = {}  # stock temporaire {email: token}

@router.post("/forgot_password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email introuvable")

    token = generate_reset_token()
    reset_tokens[request.email] = token

    # Ici normalement envoyer email avec le token
    print(f"[DEBUG] Reset token pour {request.email}: {token}")

    return {"message": "Un code de réinitialisation a été envoyé à votre email"}


# --- RESET PASSWORD ---
@router.post("/reset_password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    # Vérifier si le token existe
    email = None
    for k, v in reset_tokens.items():
        if v == request.token:
            email = k
            break

    if not email:
        raise HTTPException(status_code=400, detail="Token invalide")

    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    user.password = get_password_hash(request.new_password)
    db.commit()
    del reset_tokens[email]

    return {"message": "Mot de passe modifié avec succès"}

