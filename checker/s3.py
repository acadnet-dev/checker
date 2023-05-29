from minio import Minio
from minio.error import S3Error

from config import Config

class S3API:
    def __init__(self, config: Config):
        self.config = config
        self.client = Minio(
                config.get("Minio")["Endpoint"],
                access_key=config.get("Minio")["AccessKey"],
                secret_key=config.get("Minio")["SecretKey"],
                secure=config.get("Minio")["WithSSL"]
            )

    def get_files_in_bucket(self, bucket):
        try:
            objects = self.client.list_objects(bucket, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as exc:
            print("error occurred.", exc)
            return []
    
    def download_file(self, bucket, filename):
        try:
            response = self.client.get_object(bucket, filename)
            content = response.read()
        except S3Error as exc:
            print("error occurred.", exc)
            return None
        finally:
            response.close()
            response.release_conn()

        return content
        