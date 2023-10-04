from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from unittest.mock import patch, MagicMock

from .utils import s3_file_upload


class FileUploadTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        ...

    @patch("common.utils.client")
    def test_s3_file_upload(self, client: MagicMock):
        s3 = MagicMock()
        client.return_value = s3
        s3.upload_fileobj.return_value = None
        s3.put_object_acl.return_value = None

        file = SimpleUploadedFile(
            "test.txt", b"Test File Data", content_type="text/plain"
        )

        result = s3_file_upload(file, "files")
        self.assertTrue(result[1].startswith("https://kr.object.ncloudstorage.com"))

        s3.upload_fileobj.assert_called_once()
        s3.put_object_acl.assert_called_once()
