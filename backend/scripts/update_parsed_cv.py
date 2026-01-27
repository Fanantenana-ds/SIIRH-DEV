import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # manampy backend ho ao amin'ny path

from app.db import engine
from app.utils.cv_parcer import parse_cv_text
from sqlalchemy import text
import json

def update_all_parsed_cv():
    with engine.begin() as conn:
        candidatures = conn.execute(
            text("SELECT id, raw_cv_s3, parsed_json FROM candidatures")
        ).fetchall()

        for c in candidatures:
            cv_text = c["raw_cv_s3"] or ""
            parsed_cv = parse_cv_text(cv_text)
            parsed_json_str = json.dumps(parsed_cv)

            conn.execute(
                text("UPDATE candidatures SET parsed_json = :parsed WHERE id = :id"),
                {"parsed": parsed_json_str, "id": c["id"]}
            )

    print("✅ Tous les CV ont été parsés et mis à jour.")

if __name__ == "__main__":
    update_all_parsed_cv()
