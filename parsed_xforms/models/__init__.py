from parsed_instance import xform_instances, ParsedInstance
from registration import Registration
from data_dictionary import DataDictionary, ColumnRename
from instance_modification import InstanceModification
import common_tags


def create_xform_and_data_dictionary(path_to_xls_file, id_string=None):
    from pyxform.builder import create_survey_from_path
    from xform_manager.models import XForm
    import json

    survey = create_survey_from_path(path_to_xls_file)
    if id_string is not None:
        survey.set_id_string(id_string)
    xform = XForm.objects.create(xml=survey.to_xml())
    json_str = json.dumps(survey.to_dict())
    DataDictionary.objects.create(xform=xform, json=json_str)
