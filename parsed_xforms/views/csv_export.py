import codecs
import os
import re
import glob

class CsvWriter(object):
    """
    The csv library doesn't handle unicode strings, so we've written
    our own here.

    This class takes a generator function to iterate through all the
    dicts of data we wish to write to csv. This class also takes a key
    comparator (for sorting the keys), and a function to rename the
    headers.
    """
    def __init__(self):
        self._dict_iterator = []
        self._keys = []
        self._key_comparator = cmp
        self._key_rename_function = lambda x: x

    def set_generator_function(self, generator_function):
        """
        Unfortunately there doesn't seem to be a way to rewind a
        generator, so instead of just passing a generator as my
        dict_iterator, I'm passing the generator function so we can
        get a new generator after we run through the first.
        """
        self._generator_function = generator_function
        self._reset_dict_iterator()
        self._create_list_of_keys()

    # def set_dict_iterator(self, dict_iterator):
    #     self._dict_iterator = dict_iterator
    #     self._create_list_of_keys()

    def _reset_dict_iterator(self):
        self._dict_iterator = self._generator_function()

    def _create_list_of_keys(self):
        key_set = set()
        for d in self._dict_iterator:
            for k in d.iterkeys():
                key_set.add(k)
        self._keys = list(key_set)
        self._reset_dict_iterator()

    def set_key_comparator(self, key_comparator):
        self._key_comparator = key_comparator

    def _sort_keys(self):
        self._keys.sort(cmp=self._key_comparator)

    def set_key_rename_function(self, key_rename_function):
        self._key_rename_function = key_rename_function

    def _ensure_directory_exists(self, path):
        abspath = os.path.abspath(path)
        directory = os.path.dirname(abspath)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def write_to_file(self, path):
        self._ensure_directory_exists(path)
        self._file_object = codecs.open(path, mode="w", encoding="utf-8")

        self._sort_keys()
        headers = [self._key_rename_function(k) for k in self._keys]
        self._write_row(headers)

        for d in self._dict_iterator:
            # todo: figure out how to use csv.writer with unicode
            self._write_row([d.get(k, u"n/a") for k in self._keys])
        self._reset_dict_iterator()

        self._file_object.close()

    def _write_row(self, row):
        quote_escaped_row = []
        for cell in row:
            cell_string = unicode(cell)
            cell_string = re.sub(ur"\s+", u" ", cell_string)
            if u',' in cell_string:
                quote_escaped_row.append(u'"%s"' % cell_string)
            else:
                quote_escaped_row.append(cell_string)
        row_string = u",".join(quote_escaped_row)
        self._file_object.writelines([row_string, u"\n"])


from xform_manager.models import XForm
from parsed_xforms.models import xform_instances
from common_tags import XFORM_ID_STRING


class XFormWriter(CsvWriter):

    def __init__(self):
        super(XFormWriter, self).__init__()
        self._xform = None

    def set_xform(self, xform):
        self._xform = xform

        generator_function = self.get_data_for_csv_writer
        self.set_generator_function(generator_function)

    def get_data_for_csv_writer(self):
        match_id_string = {XFORM_ID_STRING: self._xform.id_string}
        dicts = xform_instances.find(spec=match_id_string)
        for d in dicts:
            yield d

    def set_from_id_string(self, id_string):
        xform = XForm.objects.get(id_string=id_string)
        self.set_xform(xform)

    def get_default_file_path(self):
        this_directory = os.path.dirname(__file__)
        id_string = self._xform.id_string
        return os.path.join(this_directory, "csvs", id_string + ".csv")


from parsed_xforms.models import DataDictionary


class DataDictionaryWriter(CsvWriter):

    def __init__(self):
        super(DataDictionaryWriter, self).__init__()
        self._data_dictionary = None

    def set_data_dictionary(self, data_dictionary):
        self._data_dictionary = data_dictionary

        key_rename_function = data_dictionary.get_variable_name
        self.set_key_rename_function(key_rename_function)

    def write_to_file(self, path):
        self._ensure_directory_exists(path)
        self._file_object = codecs.open(path, mode="w", encoding="utf-8")

        headers = [self._key_rename_function(k) for k in self._data_dictionary.get_headers()]
        self._write_row(headers)

        for d in self._data_dictionary.get_data_for_excel():
            # todo: figure out how to use csv.writer with unicode
            self._write_row([d.get(k, u"n/a") for k in self._data_dictionary.get_headers()])

        self._file_object.close()

    def set_from_id_string(self, id_string):
        dd = DataDictionary.objects.get(xform__id_string=id_string)
        self.set_data_dictionary(dd)

    def get_default_file_path(self):
        this_directory = os.path.dirname(__file__)
        id_string = self._data_dictionary.xform.id_string
        return os.path.join(this_directory, "csvs", id_string + ".csv")


# http://djangosnippets.org/snippets/365/
from django.http import HttpResponse, HttpResponseNotFound
from django.core.servers.basehttp import FileWrapper


def send_file(path, content_type):
    """
    Send a file through Django without loading the whole file into
    memory at once. The FileWrapper will turn the file object into an
    iterator for chunks of 8KB.
    """
    wrapper = FileWrapper(file(path))
    response = HttpResponse(wrapper, content_type=content_type)
    response['Content-Length'] = os.path.getsize(path)
    return response


from deny_if_unauthorized import deny_if_unauthorized
from django.conf import settings

@deny_if_unauthorized()
def csv_export(request, id_string):
    try:
        writer = DataDictionaryWriter()
        writer.set_from_id_string(id_string)
    except DataDictionary.DoesNotExist:
        writer = XFormWriter()
        writer.set_from_id_string(id_string)
    file_path = writer.get_default_file_path()
    writer.write_to_file(file_path)
    return send_file(path=file_path, content_type="application/csv")

## Below is AD's attempt at pulling from cached CSV files.
## uses "generate_cached_export" management command
PATH_TO_CSV_CACHE_DIRECTORY = os.path.join(
            settings.PROJECT_ROOT,
            "parsed_xforms",
            "csv_cache")

@deny_if_unauthorized()
def cached_csv_export(request, id_string, file_format):
    """
    this handles requests for an xform's downloadable CSV summary.

    it checks to see if a cached version of the spreadsheet exists.
       if it does, it returns it to the user.
       if it does not, it creates it and returns it to the user.
       *IF the cached file is out-of-date:
            it spawns a subprocess to generate a new one
    """
    # 2 file formats acceptable at the moment-- csv and csv.gz
    if file_format == "csv":
        content_type = "application/csv"
    elif file_format == "csv.gz":
        content_type = "application/gzip"
    else:
        return HttpResponseNotFound("File format not found: %s" % file_format)
    xform = XForm.objects.get(id_string=id_string)

    # gets timestamp to see if cache is out of date. see "id_stamp_for_recent_survey_cache_file"
    recent_survey_id_stamp = id_stamp_for_recent_survey_cache_file(xform)
    if recent_survey_id_stamp is None:
        return HttpResponseNotFound("No surveys to export for form: %s" % id_string)

    cached_file_root = os.path.join(PATH_TO_CSV_CACHE_DIRECTORY, \
                                            id_string, \
                                            recent_survey_id_stamp)
    cached_file_path = "%s.%s" % (cached_file_root, file_format)
    try:
        most_recent_cached_file_path = most_recent_cache(xform.id_string, file_format)
    except NotGeneratedError, e:
        from django.core.management import call_command
        call_command('generate_cached_export', xform.id_string)
        most_recent_cached_file_path = most_recent_cache(xform.id_string, file_format)
    if cached_file_path == most_recent_cached_file_path:
        return send_file(path=cached_file_path, content_type=content_type)
    else:
        #start a subprocess to generate a new one, because the current one is old.
        import subprocess
        subprocess.Popen(['python', 'manage.py', 'generate_cached_export', xform.id_string])
        return send_file(path=most_recent_cached_file_path, content_type=content_type)


class NotGeneratedError(Exception):
    pass

def most_recent_cache(xform_id_string, file_format):
    """
    glob.glob's the xform's cache dir to see if any cached versions
    already exist.

    returns the most recent one (by alphabetical order)
     - or -
    raises a custom exception if no cached versions exist.
    """
    cache_file_dir = os.path.join(PATH_TO_CSV_CACHE_DIRECTORY, xform_id_string)
    if not os.path.exists(cache_file_dir):
        raise NotGeneratedError()
    file_matches = glob.glob(os.path.join(cache_file_dir, '*.%s' % file_format))
    if len(file_matches) == 0:
        raise NotGeneratedError()
    file_matches.sort() #is this necessary?
    return file_matches[-1]

def id_stamp_for_recent_survey_cache_file(xform):
    """
    uses the xform's most recent survey to determine the timestamp
    for the cached CSV file. (when this value changes, the CSV is out of date)
    """
    try:
        most_recent_survey = xform.surveys.order_by('-date_created')[0]
    except IndexError:
        return None
    return most_recent_survey.date_created.strftime("%Y_%m_%d_%H")
