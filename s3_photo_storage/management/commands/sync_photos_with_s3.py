from django.core.management.base import BaseCommand
from django.conf import settings

from amazons3.django import S3Storage
from s3_photo_storage.models import SurveyPhoto
import glob
import os
import re

class Command(BaseCommand):
    help = "Sync photos with the local database."

    def handle(self, *args, **kwargs):
        s3s = S3Storage()
        for photo in SurveyPhoto.objects.filter(uploaded=False).all()[0:1000]:
            photo.send_to_s3(s3s)