import json
from django.db import models
from xform_manager.models import XForm
from pyxform import QuestionTypeDictionary, SurveyElementBuilder
from pyxform.section import Section
from pyxform.question import Option
from common_tags import XFORM_ID_STRING, ID
from parsed_xforms.models import xform_instances, ParsedInstance
import re


class DataDictionary(models.Model):
    xform = models.ForeignKey(XForm, related_name="data_dictionary")
    json = models.TextField()
    variable_names_json = models.TextField(default=u"{}")

    class Meta:
        app_label = "parsed_xforms"

    def __unicode__(self):
        return self.xform.__unicode__()

    def get_survey_object(self):
        if not hasattr(self, "_survey"):
            qtd = QuestionTypeDictionary("nigeria")
            builder = SurveyElementBuilder(question_type_dictionary=qtd)
            self._survey = builder.create_survey_element_from_json(self.json)
        return self._survey

    def get_survey_elements(self):
        return self.get_survey_object().iter_children()

    def _rename_state_or_lga_xpath(self, key):
        m = re.search("^(location/)?(state|lga)_in_[^/]+$", key)
        if m:
            return m.group(2)

    def get_headers(self):
        """
        Return a list of headers for a csv file.
        """
        headers = []
        for e in self.get_survey_elements():
            if isinstance(e, Section) or isinstance(e, Option):
                continue

            state_or_lga_key = self._rename_state_or_lga_xpath(
                e.get_abbreviated_xpath()
                )
            if state_or_lga_key is not None:
                if state_or_lga_key not in headers:
                    headers.append(state_or_lga_key)
            elif e.get_bind().get(u"type") == u"select":
                for child in e.get_children():
                    headers.append(child.get_abbreviated_xpath())
            else:
                headers.append(e.get_abbreviated_xpath())
        return headers

    def get_element(self, abbreviated_xpath):
        if not hasattr(self, "_survey_elements"):
            self._survey_elements = {}
            for e in self.get_survey_elements():
                self._survey_elements[e.get_abbreviated_xpath()] = e

        def remove_all_indices(xpath):
            return re.sub(r"\[\d+\]", u"", xpath)

        clean_xpath = remove_all_indices(abbreviated_xpath)
        return self._survey_elements.get(clean_xpath)

    def get_label(self, abbreviated_xpath):
        e = self.get_element(abbreviated_xpath)
        # todo: think about multiple language support
        if e:
            return e.get_label()

    def _remove_unwanted_keys(self, d):
        # we will remove repeat iterations above 4
        # TODO: This will mess up the xls export.
        def repeat_above_four(abbreviated_xpath):
            m = re.search(r"\[(\d+)\]", abbreviated_xpath)
            if m:
                return int(m.group(1)) > 4
            return False
        for k in d.keys():
            if repeat_above_four(k):
                del d[k]
            e = self.get_element(k)
            if e is None:
                continue
            if e.get_bind().get(u"readonly") == u"true()":
                del d[k]

    def get_xpath_cmp(self):
        if not hasattr(self, "_xpaths"):
            self._xpaths = [e.get_abbreviated_xpath() for e in self.get_survey_elements()]

        def xpath_cmp(x, y):
            # For the moment, we aren't going to worry about repeating
            # nodes.
            new_x = re.sub(r"\[\d+\]", u"", x)
            new_y = re.sub(r"\[\d+\]", u"", y)
            if new_x == new_y:
                return cmp(x, y)
            if new_x not in self._xpaths and new_y not in self._xpaths:
                return 0
            elif new_x not in self._xpaths:
                return 1
            elif new_y not in self._xpaths:
                return -1
            return cmp(self._xpaths.index(new_x), self._xpaths.index(new_y))

        return xpath_cmp

    def get_column_key_cmp(self):
        rename_hack = {
            u"state": u"location/zone",
            u"lga": u"location/zone"
            }
        xpath_cmp = self.get_xpath_cmp()

        def column_key_cmp(x, y):
            return xpath_cmp(rename_hack.get(x, x), rename_hack.get(y, y))

        return column_key_cmp

    def _simple_get_variable_name(self, abbreviated_xpath):
        """
        If the abbreviated_xpath has been renamed in
        self.variable_names_json return that new name, otherwise
        return the original abbreviated_xpath.
        """
        if not hasattr(self, "_variable_names"):
            self._variable_names = json.loads(self.variable_names_json)
            assert type(self._variable_names) == dict
        if abbreviated_xpath in self._variable_names and \
                self._variable_names[abbreviated_xpath]:
            return self._variable_names[abbreviated_xpath]
        return abbreviated_xpath

    def get_variable_name(self, abbreviated_xpath):
        if self._rename_select_all_option_key(abbreviated_xpath):
            return self._rename_select_all_option_key(abbreviated_xpath)
        return self._simple_get_variable_name(abbreviated_xpath)

    def get_parsed_instances_from_mongo(self):
        id_string = self.xform.id_string
        match_id_string = {XFORM_ID_STRING : id_string}
        return xform_instances.find(spec=match_id_string)

    def _rename_state_and_lga_keys(self, d):
        for key, value in d.iteritems():
            new_key = self._rename_state_or_lga_xpath(key)
            if new_key is not None:
                assert new_key not in d
                d[new_key] = d.pop(key)

    def _expand_select_all_that_apply(self, d):
        for key in d.keys():
            e = self.get_element(key)
            if e and e.get_bind().get(u"type") == u"select":
                options_selected = d[key].split()
                for i, child in enumerate(e.get_children()):
                    new_key = child.get_abbreviated_xpath()
                    if child.get_name() in options_selected:
                        assert new_key not in d
                        d[new_key] = True
                    else:
                        d[new_key] = False
                del d[key]

    def _rename_select_all_option_key(self, hacky_name):
        """
        hacky_name is the abbreviated xpath to the select all that
        apply question with an index appended to the end indicating
        the index of this child.
        """
        m = re.search(r"^(.+)\[(\d+)\]$", hacky_name)
        if m:
            e = self.get_element(m.group(1))
            if e and e.get_bind().get(u"type")==u"select":
                child = e.get_children()[int(m.group(2))]
                return child.get_abbreviated_xpath()
        return None

    def _remove_index_from_first_instance_of_repeat(self, d):
        candidates = [k for k in d.keys() if u"[1]" in k]
        for key in candidates:
            new_key = re.sub(r"\[1\]", "", key)
            assert new_key not in d
            d[new_key] = d[key]
            del d[key]

    def _add_list_of_potential_duplicates(self, d):
        parsed_instance = ParsedInstance.objects.get(instance__id=d[ID])
        if parsed_instance.phone is not None and \
                parsed_instance.start_time is not None:
            qs = ParsedInstance.objects.filter(
                phone=parsed_instance.phone,
                start_time=parsed_instance.start_time
                ).exclude(id=parsed_instance.id)
            d['_potential_duplicates'] = \
                ';'.join([str(pi.instance.id) for pi in qs])

    def get_data_for_excel(self):
        for d in self.get_parsed_instances_from_mongo():
            self._remove_index_from_first_instance_of_repeat(d)
            self._rename_state_and_lga_keys(d)
            self._expand_select_all_that_apply(d)
            self._remove_unwanted_keys(d)
            self._add_list_of_potential_duplicates(d)
            yield d
