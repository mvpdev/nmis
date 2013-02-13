from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from facilities.models import Facility, Variable, Sector
from nga_districts.models import LGA

import csv
import json
import os
import shutil
from optparse import make_option

RAISE_EXPORT_ERRORS = False

class Command(BaseCommand):
    help = "Export the lgas/facilities into json files for the nmis_ui static data viewer."
    # sectors = ['health', 'education', 'water']
    # export_types = ['facilities', 'lgas']

    option_list = BaseCommand.option_list + (
        # make_option("-s", "--sector",
        #             dest="sector",
        #             default=None,
        #             help="Specify the sector to export (only applies when exporting facilities)",
        #             action="store"),
        )

    def handle(self, *args, **kwargs):
        root_dir = "nmis_ui_data"
        if os.path.exists(root_dir):
            shutil.rmtree(root_dir)
        os.mkdir(root_dir)
        lgas = LGA.objects.filter(data_available=True, data_loaded=True)
        os.mkdir(os.path.join(root_dir, "districts"))
        os.mkdir(os.path.join(root_dir, "geo"))
        os.mkdir(os.path.join(root_dir, "presentation"))
        os.mkdir(os.path.join(root_dir, "variables"))
        export_schema("nmis_ui_data/schema.json")
        export_default_sector_data("nmis_ui_data/presentation/sectors.json")

        with open("nmis_ui_data/presentation/summary_sectors.json", 'w') as f:
            f.write(json.dumps(lga_summary_sectors_obj()))

        export_default_variables_data("nmis_ui_data/variables/variables.json")
        with open("nmis_ui_data/presentation/facilities.json", "w") as f:
            prof_indicator_ids = _profile_indicator_ids()
            fac_presentation_obj = {"profile_indicator_ids": prof_indicator_ids}
            f.write(json.dumps(fac_presentation_obj))
        export_districts("nmis_ui_data/geo/districts.json", lgas)


def _profile_indicator_ids():
    return ["chairman_name", "secretary_name", "pop_population", "area_sq_km", "state_capital_distance"]

from display_defs.models import FacilityTable, MapLayerDescription
from utils.csv_reader import CsvReader

from uis_r_us.indicators.mdg import tmp_get_mdg_indicators
from uis_r_us.indicators.facility import tmp_facility_indicators
from uis_r_us.indicators.gap_analysis import all_gap_indicators
from uis_r_us.indicators.overview import tmp_variables_for_sector, read_overview_sectors_json

def export_default_sector_data(filename):
    ftos = [s.display_dict for s in FacilityTable.objects.all()]
    with open(filename, 'w') as f:
        f.write(json.dumps({'sectors':ftos}))

def export_default_variables_data(filename):
    sectors = []
    for sector_table in FacilityTable.objects.all():
        sectors.append(sector_table.display_dict)
    overview_csv = CsvReader(os.path.join(settings.PROJECT_ROOT, "data","table_definitions", "overview.csv"))
    overview_data = list(overview_csv.iter_dicts())
    variable_slugs = []

    for item in overview_data:
        if "slug" in item.keys():
            variable_slugs.append(item["slug"])
        else:
            if RAISE_EXPORT_ERRORS:
                raise Exception("No Slug found in this item: %s" % json.dumps(item))

    profile_variables = []

    def append_variable_details(variable_slug):
        variable_slugs.append(variable_slug)
    
    for varslug in _get_ofo_list(True):
        append_variable_details(varslug)
    
    for varslug in _get_mdg_indicators(True):
        append_variable_details(varslug)

    def collect_variables_from_slugs():
        out_vars = []
        for variable_slug in set(variable_slugs):
            try:
                pv = Variable.objects.get(slug=variable_slug)
                name = pv.name
                if name in ["", None]:
                    name = "%s(name=='')" % variable_slug
                vobj = {
                    "name": name,
                    "description": pv.description,
                    "data_type": pv.data_type,
                    "slug": pv.slug
                }
                out_vars.append(vobj)
            except Variable.DoesNotExist, e:
                out_vars.append({
                    "name": "Variable not found: %s" % variable_slug,
                    "description": "",
                    "slug": variable_slug,
                    "data_type": "error"
                })
        return out_vars

    for pvid in _profile_indicator_ids():
        append_variable_details(pvid)
    
    osj = read_overview_sectors_json()
    for s in ['health', 'education', 'water']:
        section_vars = []
        for section in osj.get(s, []):
            (sname, variables) = section
            for variable in variables:
                if "section_header" not in variable.keys():
                    vslug = variable.get('value', "").replace("g::", "")
                    append_variable_details(vslug)

    variables_list = overview_data + profile_variables

    with open(filename, 'w') as f:
        o = {'sectors': sectors,
            'list': collect_variables_from_slugs()}
        f.write(json.dumps(o))
    

def export_schema(location):
    obj = {"title": "Nigeria MDG Information System (NMIS)",
            "id": "nmis_ui_data_2ef92c15",
            "groupings": {"group": "State", "local": "LGA"},
            "defaults": {
                "presentation/sectors": [
                    "presentation/sectors.json"
                ],
                "presentation/summary_sectors": [
                    "presentation/summary_sectors.json"
                ],
                "geo/districts": [
                    "geo/districts.json"
                ],
                "presentation/facilities": [
                    "presentation/facilities.json"
                ],
                "variables/variables": [
                    "variables/variables.json"
                ]
            },
            "map_layers": "map_layers.json"}
    with open(location, 'w') as f:
        f.write(json.dumps(obj))


def _profile_variables(_g):
    return [
        ["LGA Chairman", _g("chairman_name")],
        ["LGA Secretary", _g("secretary_name")],
        ["Population (2006)", _g("pop_population")],
        ["Area (square km)", _g("area_sq_km")],
        ["Distance from capital (km)", _g("state_capital_distance")],
    ]

# def lga_summary_obj(lga, data_for_display):
#     def g(slug):
#         return data_for_display.get(slug, None)
#     def pluck_val(slug):
#         v = g(slug)
#         if v["value"]:
#             return v["value"]
#         else:
#             return None
# 
# 
#     def lga_sector_definitions():
#         o = {"id": "overview",
#                 "name": "Overview",
#                 "modules": ["overview_and_map",
#                             "overview_facility_overview",
#                             "overview_mdg_status"]}
#         hlt = {"id": "health",
#                 "name": "Health",
#                 "modules": ["sector_overview", "sector_gap"]}
#         edu = {"id": "education",
#                 "name": "Education",
#                 "modules": ["sector_overview", "sector_gap"]}
#         h20 = {"id": "water",
#                 "name": "Water",
#                 "modules": ["sector_overview", "sector_gap"]}
#         return [o, hlt, edu, h20]
# 
#     def lga_summary_data(lga):
#         def overview_summary_data():
#             omods = {}
#             omsections = _profile_variables(g)
#             # omsections = _profile_variables(pluck_val)
#             omods["overview_and_map"] = omsections
#             osections = []
#             for sid, name, indicators, count  in tmp_facility_indicators(lga, data_for_display):
#                 osections.append({"name": name, "rows": indicators})
#             omods["overview_facility_overview"] = {'columns': osections}
#             return omods
#         def health_summary_data():
#             mods = {}
#             return mods
#         def education_summary_data():
#             mods = {}
#             return mods
#         def water_summary_data():
#             mods = {}
#             return mods
#         return {"overview": overview_summary_data(), \
#                 "health": health_summary_data(), \
#                 "education": education_summary_data(), \
#                 "water": water_summary_data()}
# 
#     # def lga_summary_overview_data(lga):
#     #     return [["LGA Chairman","Doctor Sam C Ugwu"], \
#     #         ["LGA Secretary","Sylvester O Ugwuagbo"], \
#     #         ["Population (2006)","148597"], \
#     #         ["Area (square km)","327.1"], \
#     #         ["Distance from capital (km)","45"]]
#     def lga_mdg_status_data(lga):
#         return tmp_get_mdg_indicators(data_for_display, g)
# 
# 
#     return {"view_details": lga_sector_definitions(), \
#                 "data": lga_summary_data(lga), \
#                 # "overview": lga_summary_overview_data(lga), \
#                 "mdg_status": lga_mdg_status_data(lga)}

class RetKey(dict):
    def get(self, key, dflt=None):
        return key
    def __getitem__(self, key):
        return key

def _get_ofo_list(only_variable_slugs=False):
    outarr = []
    summary_overview_indicator_list = tmp_facility_indicators(False, RetKey(), False)
    variable_slug_list = []
    for zzrow in summary_overview_indicator_list:
        (sslug, sname, inds, unk) = zzrow
        ss = {"name": sname}
        rows = []
        for name, vslug in inds:
            variable_slug_list.append(vslug)
            rows.append(vslug)
        ss["rows"] = rows
        outarr.append(ss)

    if only_variable_slugs:
        return variable_slug_list
    else:
        return outarr

def _get_overview_sectors_structure():
    out_obj = {}
    
    osj = read_overview_sectors_json()
    for s in ['health', 'education', 'water']:
        section_vars = []
        sector_sections = []
        for section in osj.get(s, []):
            (sname, variables) = section
            id_rows = []
            for variable in variables:
                if "section_header" in variable.keys():
                    id_rows.append(variable)
                else:
                    vslug = variable.get('value', "").replace("g::", "")
                    id_rows.append(vslug)
                    try:
                        matching_var = Variable.objects.get(slug=vslug)
                        # matching_names = Variable.objects.filter(name=variable.get('name'))
                    except Variable.DoesNotExist, e:
                        if RAISE_EXPORT_ERRORS:
                            raise Exception("Variable not found: [%s] %s" % (vslug, json.dumps(variable)))
            sector_sections.append({
                "idRows": id_rows,
                "name": sname
            })
    
        out_obj[s] = sector_sections
    return out_obj

# tmp_get_mdg_indicators
def _get_mdg_indicators(only_variable_slugs=False):

    def repeat_back(slug): return slug

    arr_o = []
    vslugs = []
    for mdg, rows in tmp_get_mdg_indicators({}, repeat_back):
        ind_ids = []
        for a, name, slug in rows:
            ind_ids.append(slug)
            vslugs.append(slug)

        arr_o.append({
            "header": mdg,
            "rows": ind_ids
        })
    if only_variable_slugs:
        return list(set(vslugs))
    else:
        return arr_o

def lga_summary_sectors_obj():
    obj = {}
    obj["view_details"] = [{u'modules': [u'overview_and_map', u'overview_facility_overview', u'overview_mdg_status'], u'id': u'overview', u'name': u'Overview'}, {u'modules': [u'sector_overview', u'sector_gap'], u'id': u'health', u'name': u'Health'}, {u'modules': [u'sector_overview', u'sector_gap'], u'id': u'education', u'name': u'Education'}, {u'modules': [u'sector_overview', u'sector_gap'], u'id': u'water', u'name': u'Water'}]
    obj["relevant_data"] = {
          "overview": {
              "overview_and_map": {"ids": _profile_indicator_ids()},
              "overview_facility_overview": {"columns": _get_ofo_list() },
              "overview_mdg_status": _get_mdg_indicators()
          }
      }
    obj["sectors"] = _get_overview_sectors_structure()
    return obj

from facilities.views import facilities_dict_for_site
def export_district(directory, district):
    os.mkdir(directory)

    lga_fac_obj = facilities_dict_for_site(district)
    lga = district
    data_for_display = lga.get_latest_data(for_display=True, display_options={
                'num_skilled_health_providers_per_1000': {'decimal_places': 3},
                'num_chews_per_1000': {'decimal_places': 3},
            })

    facs = lga_fac_obj['facilities']
    profile_data = lga_fac_obj['profileData']
    
    for subdir in ['presentation', 'data']:
        os.mkdir(os.path.join(directory, subdir))
    
    with open("%s/data/facilities.json" % directory, 'w') as f:
        f.write(json.dumps(facs))

    # with open("%s/summary.json" % directory, 'w') as f:
    #     f.write(json.dumps(lga_summary_obj(district, data_for_display)))

    profile_data_list = []
    for key, val in profile_data.items():
        item = val.copy()
        item['id'] = key
        profile_data_list.append(item)

    with open("%s/data/lga_data.json" % directory, 'w') as f:
        f.write(json.dumps({'data': profile_data_list}))

    print "Exported district: '%s'" % district.unique_slug

def export_districts(location, lgas):
    states = []
    for lga in lgas:
        if lga.state not in states:
            states.append(lga.state)
    def lga_to_obj(lga):
        o = {"group": lga.state.slug, \
            }
        o['name'] = lga.name
        o['local_id'] = lga.slug
        o['url_code'] = "%s/%s" % (lga.state.slug, lga.slug)
        o['lat_lng'] = lga.latlng_str
        lga_data_root = "districts/%s" % lga.unique_slug
        o['data_root'] = lga_data_root
        files = {}
        for jf in ["data/%s" % m for m in ["facilities", "lga_data"]]:
            files[jf] = "%s.json" % jf
        o['files'] = files
        export_district("nmis_ui_data/%s" % lga_data_root, lga)
        return o

    zones = []
    def state_to_obj(state):
        o = {"id": state.slug,
            # "group": state.zone.slug,
            "label": state.name}
        if hasattr(state, "zone"):
            if state.zone not in zones: zones.append(state.zone)
            o["group"] = state.zone.slug
        return o

    groupData = [state_to_obj(s) for s in states] + \
                [state_to_obj(z) for z in zones]

    obj = {'districts': [lga_to_obj(l) for l in lgas],
            'groups': groupData}

    with open(location, 'w') as f:
        f.write(json.dumps(obj))
