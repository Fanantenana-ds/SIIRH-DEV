import os
from minio import Minio
from minio.error import S3Error
from typing import Union
import tempfile

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "siirh-candidatures")

def _minio_client():
    if not MINIO_ENDPOINT:
        return None
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

def upload_to_minio(object_name: str, fileobj) -> str:
    """
    Accepts UploadFile.file (a file-like object). Returns object name string for DB.
    """
    client = _minio_client()
    if client:
        # ensure bucket exists
        found = client.bucket_exists(MINIO_BUCKET)
        if not found:
            client.make_bucket(MINIO_BUCKET)
        # write to temp then put
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(fileobj.read())
        tmp.flush()
        tmp.close()
        try:
            client.fput_object(MINIO_BUCKET, object_name, tmp.name)
            return f"{MINIO_BUCKET}/{object_name}"
        finally:
            try:
                os.unlink(tmp.name)
            except:
                pass
    else:
        # fallback: save under uploads/
        from pathlib import Path
        p = Path("uploads")
        p.mkdir(exist_ok=True)
        local = p / object_name
        with open(local, "wb") as f:
            fileobj.seek(0)
            f.write(fileobj.read())
        return str(local)

def fetch_bytes_flexible(objref: str) -> bytes:
    """
    objref can be:
     - minio object name like "bucket/objname" or "email_ingest/xxx.pdf"
     - local path string
     - url (http...)
    """
    if objref.startswith("http://") or objref.startswith("https://"):
        import requests
        r = requests.get(objref, timeout=15)
        r.raise_for_status()
        return r.content
    client = _minio_client()
    if client and "/" in objref:
        # assume "bucket/obj"
        bucket, obj = objref.split("/", 1)
        try:
            data = client.get_object(bucket, obj)
            return data.read()
        except Exception as e:
            raise
    # fallback local file
    with open(objref, "rb") as f:
        return f.read()