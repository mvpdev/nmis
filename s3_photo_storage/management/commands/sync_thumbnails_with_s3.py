from django.core.management.base import BaseCommand
from django.conf import settings

from amazons3.django import S3Storage
from s3_photo_storage.models import SurveyPhoto
import glob
import os
import re
import shutil

THUMBNAIL_DIRECTORY = "temp_thumbnails"

class Command(BaseCommand):
    help = "Sync photos with the local database."

    def handle(self, *args, **kwargs):
        if os.path.exists(THUMBNAIL_DIRECTORY):
            shutil.rmtree(THUMBNAIL_DIRECTORY)
        os.mkdir(THUMBNAIL_DIRECTORY)
        s3s = S3Storage()
        for photo in SurveyPhoto.objects.filter(thumbnail_uploaded=False).all()[0:1000]:
            filepath = os.path.join(THUMBNAIL_DIRECTORY, "%s.jpg" % photo.id)
            photo.sync_thumbnail(s3s)
