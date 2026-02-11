"""Ajout table offres et relation candidatures idempotent"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '168012574cee'
down_revision = None  # Raha misy migration teo aloha dia ovay eto
branch_labels = None
depends_on = None

def table_exists(table_name):
    """Check if table already exists in DB."""
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    return table_name in inspector.get_table_names()

def upgrade():
    # --- Création table offres ---
    if not table_exists('offres'):
        op.create_table(
            'offres',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('titre', sa.String(255), nullable=False),
            sa.Column('description', sa.Text),
            sa.Column('date_creation', sa.Date, nullable=True)
        )
        print("✅ Table 'offres' voaforona.")
    else:
        print("⚠️ Table 'offres' efa misy, tsy atao indray.")

    # --- Création table candidatures ---
    if not table_exists('candidatures'):
        op.create_table(
            'candidatures',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('offre_id', sa.Integer, sa.ForeignKey('offres.id', ondelete='CASCADE'), nullable=False),
            sa.Column('candidat_nom', sa.String(255), nullable=False),
            sa.Column('candidat_email', sa.String(255), nullable=False),
            sa.Column('date_candidature', sa.Date)
        )
        print("✅ Table 'candidatures' voaforona.")
    else:
        print("⚠️ Table 'candidatures' efa misy, tsy atao indray.")


def downgrade():
    # --- Supprimer tables raha mbola azo atao ---
    if table_exists('candidatures'):
        op.drop_table('candidatures')
        print("🗑️ Table 'candidatures' voafafa.")
    if table_exists('offres'):
        op.drop_table('offres')
        print("🗑️ Table 'offres' voafafa.")
