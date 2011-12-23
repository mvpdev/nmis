from django.core.management.base import BaseCommand
from django.conf import settings
from s3_photo_storage.models import SurveyPhoto
import glob
import os
import re

class Command(BaseCommand):
    help = "Sync photos with the local database."

    def handle(self, *args, **kwargs):
        for i in range(0, 100):
            istr = "*%02d.jpg" % i
            files_ending_in_i = glob.glob(os.path.join(settings.PROJECT_ROOT, "site_media", "attachments", istr))
            print "Adding %s photos to the database (count: %d)" % (istr, len(files_ending_in_i))
            for photopath in files_ending_in_i:
                photodir, photo_filename = os.path.split(photopath)
                photo_name = re.sub(".jpg", "", photo_filename)
                photo, created = SurveyPhoto.objects.get_or_create(photo_name=photo_name)
