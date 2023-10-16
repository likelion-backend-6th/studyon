import os
import uuid
from urllib.parse import quote
from datetime import datetime, timedelta

from django.apps import apps
from django.db.models import Q
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.http import HttpResponse

from boto3 import client

from manager.models import File


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
    file_name, file_ext = os.path.splitext(name)

    file_id = str(uuid.uuid4())

    file_path = f"MEDIA/{parent_directory}/{datetime.now().date()}/{file_id}{file_ext}"

    try:
        s3.upload_fileobj(file, bucket_name, file_path)
        file_url = f"{endpoint_url}/{bucket_name}/{file_path}"
        try:
            s3.put_object_acl(Bucket=bucket_name, Key=file_path, ACL="public-read")
            return file_name, file_url
        except Exception as e:
            print(f"Image setting to public failed: {e}")
    except Exception as e:
        print(f"Image upload failed: {e}")


def s3_file_download(file_id):
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

    file = get_object_or_404(File, id=file_id)

    file_key = file.url.split("https://kr.object.ncloudstorage.com/studyon/")[-1]

    s3_file_object = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_body = s3_file_object.get("Body")
    content_type = s3_file_object.get("ContentType")

    response = HttpResponse(file_body, content_type=content_type)

    encoded_filename = quote(file.name)
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{encoded_filename}.{file.url.split(".")[-1]}"'

    return response


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


class InfiniteListView(ListView):
    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page = paginator.page(page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            return (paginator, 1, [], False)
        return (paginator, page, page.object_list, page.has_other_pages())


def filter_model_data_to_delete(
    app_label,
    model_name,
    datetime_field,
    period_to_check,
    status_field,
    status_value,
    status,
):
    Model = apps.get_model(app_label=app_label, model_name=model_name)

    thirty_days_ago = datetime.now() - timedelta(days=period_to_check)

    query1 = Q(**{datetime_field + "__lt": thirty_days_ago})
    query2 = Q(**{status_field: status_value})

    filtered_data = Model.objects.filter(query1)

    if status:
        filtered_data = filtered_data.filter(query2)
    else:
        filtered_data = filtered_data.exclude(query2)

    print("delete", app_label, model_name, filtered_data)

    return filtered_data


def filter_model_data_to_change_status(
    app_label,
    model_name,
    date_field,
):
    Model = apps.get_model(app_label=app_label, model_name=model_name)

    today = datetime.now()

    query = Q(**{date_field + "__lt": today})

    filtered_data = Model.objects.filter(query)

    print("status", app_label, model_name, filtered_data)

    return filtered_data
