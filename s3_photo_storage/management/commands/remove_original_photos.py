from django.conf import settings
from s3_photo_storage.models import SurveyPhoto
import os

class Command(BaseCommand):
    help = "Remove local photos to free up space."

    def handle(self, *args, **kwargs):
        for photo in SurveyPhoto.objects.filter(uploaded=True):
            photo._remove_original_photo()
