from django.db import models
from django.conf import settings
from django.db import models
from surveyor_manager.models import Surveyor
from hashlib import md5
import os

S3_DIR_NAME = "facimg"

class FileWrapper(object):
    def __init__(self, path):
        self._path = path

    @property
    def read(self):
        return self.file.read

    def open(self):
        self.file = open(self._path, 'rb')
    
    def close(self):
        self.file.close()

class SurveyPhoto(models.Model):
    """
    keeps a record of what 
    """
    photo_name = models.CharField(max_length=100, unique=True)
    bucket_name = models.CharField(max_length=4, null=True)
    thumbnail_uploaded = models.BooleanField(default=False)
    uploaded = models.BooleanField(default=False)

    def get_bucket_name(self):
        if self.bucket_name == None:
            self.bucket_name = md5(self.photo_name).hexdigest()[0]
            self.save()
        return self.bucket_name

    @property
    def local_path(self):
        return os.path.join(settings.PROJECT_ROOT, "site_media", "attachments", "%s.jpg" % self.photo_name)

    @property
    def s3_path(self):
        return self._s3_size_path("0")

    def _s3_size_path(self, size="0"):
        return os.path.join(S3_DIR_NAME, self.get_bucket_name(), size, "%s.jpg" % self.photo_name)

    def send_to_s3(self, s3, size="0"):
        print "Uploading %s" % self.photo_name
        ff = FileWrapper(self.local_path)
        try:
            ff.open()
            s3.save(self.s3_path, ff)
            self.uploaded = True
            self.save()
        except Exception, e:
            print e
        finally:
            ff.close()

    def create_thumbnail(self, thumb_path, size=200):
        from PIL import Image
        im = Image.open(self.local_path)
        im.thumbnail((size, size), Image.ANTIALIAS)
        im.save(thumb_path)
        return thumb_path

    def sync_thumbnail(self, s3, thumbnail_directory="temp_thumbnails", size=200):
        print "Uploading thumbnail size:%s -- %s" % (str(size), self.photo_name)
        if s3==False:
            raise Exception("No S3")
        thumb_path = os.path.join(settings.PROJECT_ROOT, thumbnail_directory, "%s.jpg" % self.photo_name)
        ff = FileWrapper(self.create_thumbnail(thumb_path, size))
        try:
            ff.open()
            s3.save(self._s3_size_path(str(size)), ff)
            self.thumbnail_uploaded = True
            self.save()
        finally:
            ff.close()
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
