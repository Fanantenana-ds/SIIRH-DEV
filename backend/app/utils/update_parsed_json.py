import os
import json
from app.db import engine
import sqlalchemy
from app.utils.cv_parser import parse_cv_text
from app.utils.s3_upload import upload_file_to_s3

UPLOAD_DIR = "uploads/cvs"

def main():
    query = sqlalchemy.text("SELECT * FROM candidatures")
    update_query = sqlalchemy.text(
        "UPDATE candidatures SET parsed_json=:parsed_json, raw_cv_s3=:raw_cv_s3 WHERE id=:id"
    )

    with engine.begin() as conn:
        result = conn.execute(query)
        for row in result:
            r = dict(row._mapping)
            file_name = r.get("file_name")  # ou nom du fichier local
            file_path = os.path.join(UPLOAD_DIR, file_name)

            # 🔹 Upload automatique S3
            s3_key = f"cvs/{file_name}"
            s3_url = upload_file_to_s3(file_path, s3_key)

            # 🔹 Parse automatique du CV
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            parsed = parse_cv_text(text)

            # 🔹 Update DB
            conn.execute(update_query, {"parsed_json": json.dumps(parsed), "raw_cv_s3": s3_url, "id": r["id"]})

    print("✅ Tous les parsed_json ont été mis à jour avec succès.")

if __name__ == "__main__":
    main()
