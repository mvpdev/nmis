from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from display_defs.models import FacilityTable, MapLayerDescription
from nga_districts.models import LGA, Zone, State
from django.db.models import Count
import json
from facilities.models import FacilityRecord, Variable, LGAIndicator

from uis_r_us.indicators.gap_analysis import all_gap_indicators
from uis_r_us.indicators.overview import tmp_variables_for_sector
from uis_r_us.indicators.mdg import tmp_get_mdg_indicators
from uis_r_us.indicators.facility import tmp_facility_indicators

def _get_state_lga_from_first_two_items(arr):
    try:
        state = State.objects.get(slug=arr[0])
        full_id = '_'.join([arr[0], arr[1]])
        lga = state.lgas.get(unique_slug=full_id)
    except Exception, e:
        return (False, False, False)
    return (state, lga, True)

@login_required
def nmis_view(request, state_id, lga_id, reqpath=""):
    context = RequestContext(request)
    context.jsmodules = ['tabulations', 'facility_tables']
    context.url_root = "/nmis~/"
    context.reqpath = reqpath
    context.include_sectors = \
                ['overview', 'health', 'education', 'water']
    context.sector_data = json.dumps(sector_data())
    try:
        context.state = State.objects.get(slug=state_id)
        full_id = '_'.join([state_id, lga_id])
        context.lga = context.state.lgas.get(unique_slug=full_id)
    except Exception, e:
        return HttpResponseRedirect("/")
    lga_data = context.lga.get_latest_data(for_display=True)
    data_for_display = context.lga.get_latest_data(for_display=True, display_options={
                'num_skilled_health_providers_per_1000': {'decimal_places': 3},
                'num_chews_per_1000': {'decimal_places': 3},
            })

    def g(slug):
        return lga_data.get(slug, None)
    context.profile_data = _profile_variables(g)
    context.facility_indicators = tmp_facility_indicators(context.lga, data_for_display)
    context.mdg_indicators = tmp_get_mdg_indicators(lga_data, g)
    record_counts = FacilityRecord.counts_by_variable(context.lga.id)
    def _gap_variables(ss, lga_data):
        return []
    context.sectors = [ \
        [s, tmp_variables_for_sector(s, lga_data, record_counts), _gap_variables(s, lga_data)] \
            for s in ['health', 'education', 'water']]
    return render_to_response("nmis_view.html", context_instance=context)

def summary_views(request, lga_id, sector_id=""):
    context = RequestContext(request)
    try:
        lga = LGA.objects.get(unique_slug=lga_id)
    except Exception, e:
        return HttpResponseBadRequest("Not cool")
    context.lga = lga
    return render_to_response("summary_view.html")

@login_required
def dashboard(request, reqpath):
    if request.method == "POST":
        lgaid = request.POST['lga']
        try:
            lga = LGA.objects.get(unique_slug=lgaid)
            return HttpResponseRedirect("/new_dashboard/%s" % lga.unique_slug)
        except LGA.DoesNotExist, e:
            return HttpResponseRedirect("/~")
    context = RequestContext(request)
    context.data_loading_count = LGA.objects.filter(data_load_in_progress=True).count()
    context.site_title = "NMIS Nigeria"
    lga = None
    context.active_districts = active_districts()
    context.nav_zones = get_nav_zones(filter_active=True)
    mls = []
    for map_layer in MapLayerDescription.objects.all():
        mls.append(model_to_dict(map_layer))
    context.layer_details = json.dumps(mls)
    if not reqpath == "":
        req_params = reqpath.split("/")
        req_lga_id = req_params[0]
        if len(req_params) > 1:
            context.sector_id = req_params[1]
        else:
            context.sector_id = None
        try:
            lga = LGA.objects.get(unique_slug=req_lga_id)
            context.lga_id = "'%s'" % lga.unique_slug
        except:
            lga = None
        if lga == None:
            return HttpResponseRedirect("/~")
    if lga == None:
        return country_view(context)
    else:
        context.lga = lga
        context.lga_id = "'%s'" % context.lga.unique_slug
        return lga_view(context)

def get_nav_zones(filter_active=False):
    zone_list = Zone.objects.all().values('id', 'name')
    zones = {}
    for zone in zone_list:
        zid = zone.pop('id')
        zone['states'] = []
        zones[zid] = zone

    state_list = State.objects.all().values('id', 'zone_id', 'name')
    if filter_active:
        lga_list = LGA.objects.annotate(facility_count=Count('facilities')). \
                        filter(facility_count__gt=0). \
                        values('unique_slug', 'name', 'state_id')
    else:
        lga_list = LGA.objects.all().values('unique_slug', 'name', 'state_id')
    states = {}
    for state in state_list:
        sid = state.pop('id')
        zid = state.pop('zone_id')
        state['lgas'] = []
        states[sid] = state
        zones[zid]['states'].append(state)
    for lga in lga_list:
        sid = lga.pop('state_id')
        states[sid]['lgas'].append(lga)
    for state in state_list:
        state['lga_count'] = len(state['lgas'])
    return zone_list

def get_nav_zones_inefficient():
    zones = Zone.objects.all()
    nav_list = []
    for zone in zones:
        nav_list.append({
            'name': zone.name,
            'states': state_data(zone)
        })
    return nav_list

def state_data(zone):
    state_l = []
    for state in zone.states.all():
        state_lgas = state.lgas.all().values('name', 'unique_slug')
        state_l.append({
            'name': state.name,
            'lgas': state_lgas
        })
    return state_l

def country_view(context):
    context.site_title = "Nigeria"
    context.breadcrumbs = [
        ("Nigeria", "/"),
    ]
    return render_to_response("ui.html", context_instance=context)

def lga_view(context):
    context.site_title = ""
    context.lga_id = "'%s'" % context.lga.unique_slug
    context.breadcrumbs = [
        ("Nigeria", "/"),
        (context.lga.state.name, "/"),
        (context.lga.name, "/new_dashboard/%s" % context.lga.unique_slug),
        ("Facility Detail", "/~%s" % context.lga.unique_slug),
    ]
    if context.sector_id is not None:
        context.breadcrumbs.append((
            context.sector_id.capitalize(),
            "/~%s/%s" % (context.lga.unique_slug, context.sector_id),
        ))
    context.local_nav_urls = get_nav_urls(context.lga, mode='facility', sector=context.sector_id)
    if context.sector_id is None:
        context.sector_id = 'overview'
    context.overview_sectors = [
        {
            'name': "Health",
            'slug': 'health',
            'count': 50
        },
        {
            'name': "Education",
            'slug': 'education',
            'count': 25
        },
        {
            'name': "Water",
            'slug': 'water',
            'count': 25
        },
    ]

    context.facilities_count = 100
    context.profile_variables = [
        ["LGA Chairman", "chairman_name"],
        ["LGA Secretary", "secretary_name"],
        ["Population (2006)", "pop_population"],
        ["Area (square km)", "area_sq_km"],
        ["Distance from capital (km)", "state_capital_distance"],
    ]
    context.local_nav = {
        'mode': {'facility': True},
        'sector': {context.sector_id: True}
    }
    return render_to_response("ui.html", context_instance=context)


from utils.csv_reader import CsvReader
import os
from django.conf import settings

def sector_data():
    return [s.display_dict for s in FacilityTable.objects.all()]

def variable_data(request):
    sectors = []
    for sector_table in FacilityTable.objects.all():
        sectors.append(sector_table.display_dict)
    overview_csv = CsvReader(os.path.join(settings.PROJECT_ROOT, "data","table_definitions", "overview.csv"))
    overview_data = []
    for z in overview_csv.iter_dicts():
        overview_data.append(z)
    return HttpResponse(json.dumps({
        'sectors': sectors,
        'overview': overview_data
    }))

def active_districts():
    lgas = LGA.objects.filter(data_loaded=True, data_available=True)
#    lgas = LGA.objects.annotate(facility_count=Count('facilities')).filter(facility_count__gt=0)
    from collections import defaultdict
    states = defaultdict(list)
    for lga in lgas:
        states[lga.state].append(lga)
        
    output = []
    for state, lgas in states.items():
        statelgas = []
        for lga in lgas:
            statelgas.append(
                (lga.name, lga.unique_slug)
                )
        output.append((state.name, statelgas))
    return output

def all_mustache_templates(request):
    import os, glob
    cur_file = os.path.abspath(__file__)
    cur_dir = os.path.dirname(cur_file)
    all_templates = glob.glob(os.path.join(cur_dir, 'mustache', '*.html'))
    templates = []
    for template_path in all_templates:
        with open(template_path, 'r') as f:
            templates.append(f.read())
    return HttpResponse('\n'.join(templates))

def mustache_template(request, template_name):
    import os
    cur_file = os.path.abspath(__file__)
    cur_dir = os.path.dirname(cur_file)
    template_path = os.path.join(cur_dir, 'mustache', '%s.html' % template_name)
    if not os.path.exists(template_path):
        return HttpResponse('{"ERROR":"No such template: %s"}' % template_name)
    else:
        with open(template_path, 'r') as f:
            return HttpResponse(f.read())

def modes(request, mode_data):
    return render_to_response("modes.html")

def google_help_doc(request):
    google_doc_zip_url = "https://docs.google.com/document/d/1Dze4IZGr0IoIFuFAI_ohKR5mYUt4IAn5Y-uCJmnv1FQ/export?format=zip&id=1Dze4IZGr0IoIFuFAI_ohKR5mYUt4IAn5Y-uCJmnv1FQ&token=AC4w5VhqxjgX9xFvekZGlLQILEIfrl1wSg%3A1312574701000&tfe=yh_186"
    cached_doc_path = os.path.join("docs", "cached_doc.html")
    if not os.path.exists(cached_doc_path):
        import urllib, zipfile
        f = urllib.urlopen(google_doc_zip_url)
        zf_path = "%s.zip" % cached_doc_path
        with open(zf_path, 'w') as foutput:
            foutput.write(f.read())
        z = zipfile.ZipFile(zf_path)
        for name in z.namelist():
            with open(cached_doc_path, 'w') as html_file:
                html_file.write(z.read(name))
    with open(cached_doc_path) as f:
        return HttpResponse(f.read())


def test_module(request, module_id):
    context = RequestContext(request)
    context.module = module_id
    context.modules = ['modes', 'tabulations', 'facility_tables']
    if module_id in context.modules:
        return render_to_response("test_module.html", context_instance=context)
    else:
        return HttpResponseRedirect("/test/modes")

def test_map(request):
    return render_to_response("test_map.html")

def get_nav_urls(lga, mode='lga', sector='overview'):
    d = {}
    if mode == "lga":
        d['overview'] = '/new_dashboard/%s' % lga.unique_slug
    else:
        d['overview'] = '/~%s' % (lga.unique_slug)
    def sector_url(sector):
        if mode == 'lga':
            return '/new_dashboard/%s/%s' % (lga.unique_slug, sector)
        else:
            return '/~%s/%s' % (lga.unique_slug, sector)
    def mode_url(mode):
        if mode == "lga":
            if sector == "overview":
                return "/new_dashboard/%s" % lga.unique_slug
            elif sector == None:
                return "/new_dashboard/%s" % lga.unique_slug
            else:
                return "/new_dashboard/%s/%s" % (lga.unique_slug, sector)
        else:
            if sector == "overview":
                return "/~%s" % lga.unique_slug
            else:
                return "/~%s/%s" % (lga.unique_slug, sector)
    sd = [(s, sector_url(s)) for s in ['health', 'education', 'water']]
    d.update(dict(sd))
    d.update(dict([(m, mode_url(m)) for m in ['lga', 'facility']]))
    return d

def new_dashboard(request, lga_id):
    context = RequestContext(request)
    try:
        lga = LGA.objects.get(unique_slug=lga_id)
    except:
        return HttpResponseRedirect("/")
    context.preview_link = "/nmis~/%s" % lga.url_id
    context.site_title = "LGA Overview"
    context.small_title = "%s, %s" % (lga.state.name, lga.name)
    context.breadcrumbs = [
        ("Nigeria", "/"),
        (lga.state.name, "/"),
        (lga.name, "/new_dashboard/%s" % lga.unique_slug),
    ]
    context.local_nav_urls = get_nav_urls(lga, mode='lga', sector='overview')
    context.local_nav = {
        'mode': {'lga': True},
        'sector': {'overview': True}
    }
    lga_data = lga.get_latest_data(for_display=True)
    def g(slug):
        return lga_data.get(slug, None)
    data_for_display = lga.get_latest_data(for_display=True, display_options={
                'num_skilled_health_providers_per_1000': {'decimal_places': 3},
                'num_chews_per_1000': {'decimal_places': 3},
            })
    context.facility_indicators = tmp_facility_indicators(lga, data_for_display)
    context.mdg_indicators = tmp_get_mdg_indicators(lga_data, g)
    context.navs = [{ 'url': '/', 'name': 'Home' },
                    { 'url': '/new_dashboard/%s' % lga.unique_slug,
                        'name': lga.name,
                        'active': True}]
    #tmp deactivating breadcrumb
    context.navs = False
    context.active_districts = active_districts()
    context.lga = lga
    context.state = lga.state
    context.profile_variables = _profile_variables(g)
    return render_to_response("new_dashboard.html", context_instance=context)

def _profile_variables(g):
    return [
        ["LGA Chairman", g("chairman_name")],
        ["LGA Secretary", g("secretary_name")],
        ["Population (2006)", g("pop_population")],
        ["Area (square km)", g("area_sq_km")],
        ["Distance from capital (km)", g("state_capital_distance")],
    ]

def new_sector_overview(request, lga_id, sector_slug):
    try:
        lga = LGA.objects.get(unique_slug=lga_id)
    except:
        return HttpResponseRedirect("/new_dashboard/")
    if sector_slug not in ["education", "health", "water"]:
        return HttpResponseRedirect("/new_dashboard/")
    sector_name = sector_slug.capitalize()
    context = RequestContext(request)
    context.active_districts = active_districts()
    context.site_title = "%s Overview" % sector_name
    context.small_title = "%s, %s" % (lga.state.name, lga.name)
    context.breadcrumbs = [
        ("Nigeria", "/"),
        (lga.state.name, "/"),
        (lga.name, "/new_dashboard/%s" % lga.unique_slug),
        ("LGA Summary", "/new_dashboard/%s" % lga.unique_slug),
        (sector_name, "/new_dashboard/%s/%s" % (lga.unique_slug, sector_slug)),
    ]
    context.local_nav = {
        'mode': {'lga': True},
        'sector': {sector_slug: True}
    }
    context.local_nav_urls = get_nav_urls(lga, mode='lga', sector=sector_slug)
    context.lga = lga
    context.lga_id = "'%s'" % context.lga.unique_slug
    context.navs = [{ 'url': '/', 'name': 'Home' },
                    { 'url': '/new_dashboard/%s' % lga.unique_slug, 'name': lga.name },
                    { 'url': '/new_dashboard/%s/%s' % (lga.unique_slug, sector_slug),
                        'name': sector_slug.capitalize(),
                        'active': True }]
    #tmp deactivating breadcrumb
    context.navs = False
    lga_data = lga.get_latest_data(for_display=True, \
        display_options={
            'num_skilled_health_providers_per_1000': {'decimal_places': 3},
            'num_chews_per_1000': {'decimal_places': 3},
            'teacher_nonteachingstaff_ratio_lga': {'decimal_places': 3},
        })
    record_counts = FacilityRecord.counts_by_variable(lga.id)
    context.table_data = tmp_variables_for_sector(sector_slug, lga_data, record_counts)
    context.sector = sector_slug
    def j(slug):
        value_dict = lga_data.get(slug, None)
        if value_dict:
            return value_dict.get('value', None)
        else:
            return 'N/A'
    def plug_in_values(row):
        for key in ['current', 'gap', 'target']:
            if key in row:
                row[key] = j(row[key])
        return row

    context.gap_indicators = [plug_in_values(r) \
                    for r in all_gap_indicators().get(sector_slug, [])]

    return render_to_response("new_sector_overview.html", context_instance=context)
