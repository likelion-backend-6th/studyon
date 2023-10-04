import uuid
from datetime import datetime

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from boto3 import client


def s3_file_upload(upload_file: InMemoryUploadedFile, parent_directory):
    service_name = "s3"
    aws_access_key_id = settings.NCP_S3_ACCESS_KEY
    aws_secret_access_key = settings.NCP_S3_SECRET_KEY
    endpoint_url = settings.NCP_S3_ENDPOINT_URL
    bucket_name = settings.NCP_S3_BUCKET_NAME

    s3 = client(
        service_name,
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    bucket_name = bucket_name

    file = upload_file.file
    name = upload_file.name
    file_ext = name.split(".")[-1]

    file_id = str(uuid.uuid4())

    file_path = f"MEDIA/{parent_directory}/{datetime.now().date()}/{file_id}.{file_ext}"

    try:
        s3.upload_fileobj(file, bucket_name, file_path)
        file_url = f"{endpoint_url}/{bucket_name}/{file_path}"
        try:
            s3.put_object_acl(Bucket=bucket_name, Key=file_path, ACL="public-read")
            return file_url
        except Exception as e:
            print(f"Image setting to public failed: {e}")
    except Exception as e:
        print(f"Image upload failed: {e}")


class Tags:
    tag_list = ["database", "frontend", "backend", "CD/CD", "python", "비대면", "게임"]

    # for in, list() operator
    def __iter__(self):
        self.current = -1
        self.high = len(self.tag_list)
        return self

    # for in, list() operator
    def __next__(self):
        self.current += 1
        if self.current < self.high:
            return self.tag_list[self.current]
        raise StopIteration

    # in operator
    def __contains__(self, key):
        return key in self.tag_list
