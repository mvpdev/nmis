from django.core.management.base import BaseCommand
from django.core.management import call_command
from optparse import make_option
from xform_manager.models import XForm
from django.conf import settings
import os
import gzip
import shutil

from parsed_xforms.models import DataDictionary
from parsed_xforms.views.csv_export import DataDictionaryWriter, XFormWriter, \
                id_stamp_for_recent_survey_cache_file


class Command(BaseCommand):
    help = "Generate one or many csv caches for downloadable files."

    option_list = BaseCommand.option_list + (
        make_option("-a", "--all",
                    help="Generate caches for all xforms.",
                    dest="generate_all",
                    default=False,
                    action="store_true"),
        )

    def handle(self, *args, **kwargs):
        if kwargs.pop('generate_all', False):
            # "generate_all" will get all xform id strings and attempt to
            #  pass them to this "handle" method to create a cache.
            xforms = XForm.objects.all()
            id_strings = [x['id_string'] for x in xforms.values('id_string')]
            for id_string in id_strings:
                targs = (id_string, )
                self.handle(*targs, **kwargs)
            return
        assert len(args) > 0
        for arg in args:
            try:
                id_string = XForm.objects.get(id_string=arg).id_string
                kwargs['xform_id_string'] = id_string
                self.generate_for_xform(**kwargs)
            except XForm.DoesNotExist:
                continue

    CACHE_DIRECTORY = os.path.join(settings.PROJECT_ROOT, 'parsed_xforms', 'csv_cache')

    def generate_for_xform(self, **kwargs):
        id_string = kwargs.get('xform_id_string')
        assert id_string is not None

        # When writing files that are simultaneously served,
        # we need to write to a temporary directory and move stuff once it's done
        xform_dir = os.path.join(self.CACHE_DIRECTORY, id_string)
        xform_dir_new = os.path.join(self.CACHE_DIRECTORY, '.%s' % id_string)
        xform_dir_stale = os.path.join(self.CACHE_DIRECTORY, '.STALE_%s' % id_string)

        # creating cache directories if they do not exist
        if not os.path.exists(self.CACHE_DIRECTORY):
            os.mkdir(self.CACHE_DIRECTORY)
        if not os.path.exists(xform_dir_new):
            os.mkdir(xform_dir_new)

        xform = XForm.objects.get(id_string=id_string)

        # uses the same id_stamp generator as csv_export
        id_stamp = id_stamp_for_recent_survey_cache_file(xform)
        if id_stamp is None:
            # probably because zero surveys have been collected
            return

        # cached_file_root is the cached file without a file extension
        cached_file_root = os.path.join(xform_dir_new, id_stamp)

        # this code writes the CSV for a given XForm.
        # it was copied from parsed_xform.views.csv_export
        try:
            writer = DataDictionaryWriter()
            writer.set_from_id_string(id_string)
        except DataDictionary.DoesNotExist:
            writer = XFormWriter()
            writer.set_from_id_string(id_string)
        writer.write_to_file("%s.csv" % cached_file_root)

        # storing a gzipped version of the csv
        outfile = gzip.open("%s.csv.gz" % cached_file_root, 'wb')
        with open("%s.csv" % cached_file_root, 'r') as infile:
            outfile.write(infile.read())
        outfile.close()

        # removing stale cache dir if it exists, replacing with new one
        if os.path.exists(xform_dir):
            os.rename(xform_dir, xform_dir_stale)
            os.rename(xform_dir_new, xform_dir)
            shutil.rmtree(xform_dir_stale)
        else:
            os.rename(xform_dir_new, xform_dir)

