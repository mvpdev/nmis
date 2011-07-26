from django.test import TestCase
from parsed_xforms.models import create_xform_and_data_dictionary, \
    xform_instances
from xform_manager.import_tools import import_instances_from_phone
from xform_manager.models import XForm
import os
from parsed_xforms.views import csv_export
from django.core.urlresolvers import reverse
import csv
import json


class TestLgaCollapse(TestCase):

    def setUp(self):
        self.test_path = os.path.join("parsed_xforms", "tests", "zone_state_lga")
        xls_path = os.path.join(self.test_path, "survey.xls")
        self.id_string = "survey_2011_07_26"
        create_xform_and_data_dictionary(xls_path, self.id_string)
        odk_path = os.path.join(self.test_path, "odk")
        import_instances_from_phone(odk_path)
        self.assertEqual(XForm.objects.count(), 1)
        self.xform = XForm.objects.all()[0]

    def test_setup(self):
        self.assertEqual(self.xform.surveys.count(), 2)

    def test_data_dictionary_headers(self):
        l = list(self.xform.data_dictionary.all())
        self.assertTrue(len(l) == 1)
        dd = l[0]
        expected_list = ['zone', 'state', 'lga']
        self.assertEqual(dd.get_headers(), expected_list)

    def test_csv_export(self):
        url = reverse(csv_export, kwargs={'id_string': self.id_string})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        actual_csv = response.content
        actual_lines = actual_csv.split("\n")
        actual_csv = csv.reader(actual_lines)
        expected_csv = [
            ['zone', 'state', 'lga'],
            ['north_central', 'kogi', 'omala'],
            ['south_south', 'cross_river', 'odukpani'],
            ]
        for actual_row, expected_row in zip(actual_csv, expected_csv):
            for actual_cell, expected_cell in zip(actual_row, expected_row):
                self.assertEqual(actual_cell, expected_cell)
