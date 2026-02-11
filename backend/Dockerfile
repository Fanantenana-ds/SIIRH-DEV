# ==== BACKEND - FastAPI ====
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


activation et desactivatio docker:
sudo systemctl stop docker
sudo systemctl stop containerd
 reactive:
 sudo systemctl start docker
sudo systemctl start containerd



modification mdp :

[jeremi@Seraphin]
└─❯ cd /home/jeremi-seraphin/DATA/STAGE/SIIRH/backend

┌─[jeremi@Seraphin]
└─❯ export ADMIN_EMAIL="admin@rh.local"
export ADMIN_PASSWORD="Admin@RH2025!"
export ADMIN_USERNAME="admin"

python3 - <<'PY'
from app.db import create_default_admin
print(create_default_admin(force=True))
PY
⚠️ passlib/bcrypt tsy hita: ny mot de passe dia tsy ho hashé (fallback plaintext). Ho an'ny sécurité, apetraho ny passlib sy bcrypt amin'ny venv-nao.
🔁 Admin 'admin@rh.local' nohavaozina (id=1).
{'created': False, 'updated': True, 'id': 1}

┌─[jeremi@Seraphin]
└─❯ 
SIIRH123 code farany 
admin.rh@siirh.local


, efa tafiditra tsara ny PostgreSQL sy nanova ny password (Jeremi123) ianao, fa izao tsy hita ny Alembic
