from django.test import TestCase
from parsed_xforms.models import create_xform_and_data_dictionary, \
    xform_instances
from xform_manager.import_tools import import_instances_from_phone
from xform_manager.models import XForm
import os
from parsed_xforms.views import csv_export
from django.core.urlresolvers import reverse
import csv


class TestTransportationSurvey(TestCase):

    def setUp(self):
        self.test_path = os.path.join("parsed_xforms", "tests", "transportation")

        xls_path = os.path.join(self.test_path, "transportation.xls")
        self.id_string = "transportation_2011_07_25"
        create_xform_and_data_dictionary(xls_path, self.id_string)
        odk_path = os.path.join(self.test_path, "odk")
        import_instances_from_phone(odk_path)
        self.assertEqual(XForm.objects.count(), 1)
        self.xform = XForm.objects.all()[0]

    def test_setup(self):
        self.assertEqual(self.xform.id_string, "transportation_2011_07_25")
        self.assertEqual(self.xform.surveys.count(), 4)

    def test_mongo_entries(self):
        data = [
            {
                "available_transportation_types_to_referral_facility": "ambulance bicycle",
                "ambulance/frequency_to_referral_facility": "daily",
                "bicycle/frequency_to_referral_facility": "weekly"
                },
            {
                "available_transportation_types_to_referral_facility": "none"
                },
            {
                "available_transportation_types_to_referral_facility": "ambulance",
                "ambulance/frequency_to_referral_facility": "weekly",
                },
            {
                "available_transportation_types_to_referral_facility": "taxi other",
                "available_transportation_types_to_referral_facility_other": "camel",
                "taxi/frequency_to_referral_facility": "daily",
                "other/frequency_to_referral_facility": "other",
                }
            ]
        for d, mongo_entry in zip(data, xform_instances.find()):
            for k, v in d.items():
                self.assertEqual(v, mongo_entry["transportation/" + k])

    def test_group_xpaths_should_not_be_added_to_mongo(self):
        instance = self.xform.surveys.all()[0]
        expected_dict = {
            "transportation": {
                "transportation": {
                    "bicycle": {
                        "frequency_to_referral_facility": "weekly"
                        },
                    "ambulance": {
                        "frequency_to_referral_facility": "daily"
                        },
                    "available_transportation_types_to_referral_facility": "ambulance bicycle",
                    }
                }
            }
        self.assertEqual(instance.get_dict(flat=False), expected_dict)
        expected_dict = {
            "transportation/available_transportation_types_to_referral_facility": "ambulance bicycle",
            "transportation/ambulance/frequency_to_referral_facility": "daily",
            "transportation/bicycle/frequency_to_referral_facility": "weekly",
            "_xform_id_string": "transportation_2011_07_25",
            }
        self.assertEqual(instance.get_dict(), expected_dict)

    def test_csv_export(self):
        url = reverse(csv_export, kwargs={'id_string': self.id_string})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        actual_csv = response.content
        actual_lines = actual_csv.split("\n")
        actual_csv = csv.reader(actual_lines)
        f = open(os.path.join(self.test_path, "transportation.csv"), "r")
        expected_csv = csv.reader(f)
        for actual_row, expected_row in zip(actual_csv, expected_csv):
            for actual_cell, expected_cell in zip(actual_row, expected_row):
                self.assertEqual(actual_cell, expected_cell)
        f.close()

        # TODO: Specify other questions should not be collapsed into a
        # single column.

        # TODO: Headers should be determined by the survey definition,
        # not the data received.
