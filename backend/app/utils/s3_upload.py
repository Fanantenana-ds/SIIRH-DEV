# import boto3
# from botocore.exceptions import NoCredentialsError
# import os

# # ⚡ Configuration S3
# S3_BUCKET = "nom-de-votre-bucket"
# S3_REGION = "us-east-1"  # ohatra
# S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
# S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# s3_client = boto3.client(
#     "s3",
#     region_name=S3_REGION,
#     aws_access_key_id=S3_ACCESS_KEY,
#     aws_secret_access_key=S3_SECRET_KEY
# )

# def upload_file_to_s3(file_path: str, s3_key: str) -> str:
#     """
#     Upload file to S3 and return the file URL
#     """
#     try:
#         s3_client.upload_file(file_path, S3_BUCKET, s3_key)
#         url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
#         return url
#     except NoCredentialsError:
#         raise Exception("AWS credentials not found")










import boto3
from botocore.exceptions import ClientError

# 🔹 Configuration MinIO
S3_BUCKET = "cv-files"                  # Soloina amin'ny bucket-nao
S3_ENDPOINT = "http://127.0.0.1:9000"  # URL MinIO server
S3_ACCESS_KEY = "minioadmin"           # MinIO access key
S3_SECRET_KEY = "minioadmin"           # MinIO secret key

# 🔹 Initialize boto3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

def ensure_bucket_exists(bucket_name: str):
    """
    Mamorona bucket raha tsy misy
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name)

def upload_file(file_path: str, s3_key: str) -> str:
    """
    Mandefa file ao amin'ny MinIO
    :param file_path: lalana mankany amin'ny file eo an-toerana
    :param s3_key: anaran'ny file ao amin'ny bucket
    :return: URL file ao amin'ny MinIO
    """
    ensure_bucket_exists(S3_BUCKET)
    try:
        s3_client.upload_file(file_path, S3_BUCKET, s3_key)
        return f"{S3_ENDPOINT}/{S3_BUCKET}/{s3_key}"
    except ClientError as e:
        raise Exception(f"Upload failed: {e}")

def list_files(bucket_name: str):
    """
    Mamerina lisitry ny files ao amin'ny bucket
    :param bucket_name: anaran'ny bucket
    :return: lisitry ny keys
    """
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            return [obj["Key"] for obj in response["Contents"]]
        return []
    except ClientError as e:
        raise Exception(f"Listing files failed: {e}")

def download_file(s3_key: str, local_path: str):
    """
    Misintona file avy amin'ny MinIO
    :param s3_key: anaran'ny file ao amin'ny bucket
    :param local_path: lalana hotehirizina ao an-toerana
    """
    try:
        s3_client.download_file(S3_BUCKET, s3_key, local_path)
    except ClientError as e:
        raise Exception(f"Download failed: {e}")

def delete_file(s3_key: str):
    """
    Mamafa file ao amin'ny MinIO
    :param s3_key: anaran'ny file ao amin'ny bucket
    """
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
    except ClientError as e:
        raise Exception(f"Delete failed: {e}")
