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
        except:
            lga = None
        if lga == None:
            return HttpResponseRedirect("/~")
    if lga == None:
        return country_view(context)
    else:
        context.lga = lga
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
    context.local_nav = {
        'mode': {'facility': True},
        'sector': {context.sector_id: True}
    }
    return render_to_response("ui.html", context_instance=context)


from utils.csv_reader import CsvReader
import os
from django.conf import settings

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
    lgas = LGA.objects.filter(data_loaded=True)
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

def temp_facility_buildr(lga):
    lga_data = lga.get_latest_data(for_display=True, \
        display_options={
            'num_skilled_health_providers_per_1000': {'decimal_places': 3},
            'num_chews_per_1000': {'decimal_places': 3},
        })
    def g(slug):
        value_dict = lga_data.get(slug, None)
        if value_dict:
            return value_dict.get('value', None)
        else:
            return None
    def h(slug1, slug2):
        if g(slug1) == None or g(slug2) == None:
            return None
        return "%s/%s" % (g(slug1), g(slug2))
    ilist = []
    health_indicators = [
            ["Health posts and dispensaries", g("num_level_1_health_facilities")],
            ["Primary health clinics", g("num_level_2_health_facilities")],
            ["Primary health centres", g("num_level_3_health_facilities")],
            ["Comprehensive health centres & hospitals", g("num_level_4_health_facilities")],
            ["Other health facillities", g("num_level_other_health_facilities")],
            ["Facilities that perform Caesarean sections", g("num_health_facilities_c_sections")],
            ["Skilled health providers per 1,000 population ", g("num_skilled_health_providers_per_1000")],
            ["CHEWs per 1,000 population", g("num_chews_per_1000")],
        ]
    ilist.append(("health", "Health Facilities", health_indicators, g("num_health_facilities")))

    education_indicators = [
            ["Preprimary", g("num_preprimary_level")],
            ["Preprimary and primary", g("num_preprimary_primary_level")],
            ["Primary", g("num_primary_level")],
            ["Primary and junior secondary", g("num_primary_js_level")],
            ["Junior secondary", g("num_js_level")],
            ["Junior and senior secondary", g("num_js_ss_level")],
            ["Senior secondary", g("num_ss_level")],
            ["Primary, junior and senior secondary", g("num_primary_js_ss_level")],
            ["Other schools", g("num_other_level")],
            ["Pupil to teacher ratio", g("student_teacher_ratio_lga")],
            ["Percentage of teachers with NCE qualification", g("proportion_teachers_nce")],
            ["Classrooms in need of major repairs", g("number_classrooms_need_major_repair")],
        ]
    ilist.append(("education", "Schools", education_indicators, g("num_schools")))

    water_indicators = [
            ["Developed/treated spring and surface water", g("num_developed_and_treated_or_protected_surface_or_spring_water")],
            ["Protected dug wells", g("num_protected_dug_wells")],
            ["Boreholes and tube wells", g("num_boreholes_and_tubewells")],
            ["Boreholes and tube wells with non-motorized lift/pump mechanisms", g("num_boreholes_tubewells_manual")],
            ["Boreholes and tube wells with motorized lift/pump mechanisms", g("num_boreholes_tubewells_non_manual")],
            ["Well-maintained boreholes, protected and treated water sources", g("num_protected_water_sources_functional")],
            ["Population served per well-maintained borehole, protected or treated water source", g("population_served_per_protected_and_functional_water_source")],
        ]
    ilist.append(("water", "Water Points", water_indicators, g("num_water_points")))
    return ilist

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
    context.facility_indicators = temp_facility_buildr(lga)
    context.mdg_indicators = [
        ("Goal 1: Eradicate extreme poverty and hunger", [
            [None, "Percentage of children under five who are underweight (weight-for-age)", g("prevalence_of_underweight_children_u5")],
            [None, "Percentage of children under five with stunting (height-for-age)", g("prevalence_of_stunting_children_u5")],
            [None, "Percentage of children under five with wasting (weight-for-height)", g("prevalence_of_wasting_children_u5")],
        ]),
        ("Goal 2: Achieve universal primary education", [
            [None, "Net enrollment rate for primary education", g("net_enrollment_ratio_primary_education")],
            [None, "Gross enrollment rate in primary education", g("gross_enrollment_rate_primary")],
            [None, "Net enrollment rate for secondary education", g("net_enrollment_ratio_secondary_education")],
            [None, "Gross enrollment rate in secondary education", g("gross_enrollment_ratio_secondary_education")],
            [None, "Literacy rate of 15-24 year olds (men and women)", g("literacy_rate")],
        ]),
        ("Goal 3: Promote gender equality and empower women", [
            [None, "Ratio of girls to boys in primary schools", g("girl_boy_ratio_primary")],
            [None, "Ratio of girls to boys in junior secondary schools", g("girl_boy_ratio_js")],
            [None, "Ratio of girls to boys in senior secondary schools ", g("girl_boy_ratio_secondary_school")],
            [None, "Gender parity index (GPI) for primary schools", g("gender_parity_index_primary")],
            [None, "Gender parity index (GPI) for junior secondary schools", g("gender_parity_index_js")],
        ]),
        ("Goal 4: Reduce child mortality", [
            [None, "Under five mortality rate (per 1,000 live births)", g("mortality_rate_children_u5")],
            [None, "Infant mortality rate (per 1,000 live births)", g("mortality_rate_infant")],
            [None, "Measles immunization rate", g("immunization_rate_measles")],
            [None, "DPT 3 immunization rate", g("immunization_rate_dpt3")],
            [None, "Percentage of children under five years of age with diarrhea who received oral rehydration therapy", g("proportion_of_children_u5_diarrhea_treated_with_ors_med")],
        ]),
        ("Goal 5: Improve maternal health", [
            [None, "Maternal mortality", g("mortality_rate_maternal")],
            [None, "Percentage of births attended by a skilled birth attendant", g("proportion_of_births_by_skilled_health_personnel")],
            [None, "Percentage of women who attended at least four antenatal visits", g("percent_antenatal_care_four")],
            [None, "Percentage of pregnant women tested for HIV", g("percentage_pregnant_women_tested_for_hiv_during_pregnancy")],
        ]),
        ("Goal 6: Combat HIV/AIDS, malaria and other diseases", [
            [None, "HIV Prevalence", g("prevalence_of_hiv")],
            [None, "Percentage of men and women ever tested for HIV", g("percentage_of_individuals_tested_for_hiv_ever")],
            [None, "Percentage of children under five sleeping under insecticide-treated bednets", g("proportion_children_u5_sleeping_under_itns")],
            [None, "Tuberculosis treatment success rate", None],
        ]),
        ("Goal 7: Ensure environmental sustainability", [
            [None, "Percentage of households with access to an improved water source", g("percentage_households_with_access_to_improved_water_sources")],
            [None, "Percentage of households with access to improved sanitation", g("percentage_households_with_access_to_improved_sanitation")],
        ]),
    ]
    context.navs = [{ 'url': '/', 'name': 'Home' },
                    { 'url': '/new_dashboard/%s' % lga.unique_slug,
                        'name': lga.name,
                        'active': True}]
    #tmp deactivating breadcrumb
    context.navs = False
    context.lga = lga
    context.state = lga.state
    context.profile_variables = [
        ["LGA Chairman", g("chairman_name")],
        ["LGA Secretary", g("secretary_name")],
        ["Population (2006)", g("pop_population")],
        ["Area (square km)", g("area_sq_km")],
        ["Distance from capital (km)", g("state_capital_distance")],
    ]
    return render_to_response("new_dashboard.html", context_instance=context)

def tmp_variables_for_sector(sector_slug, lga):
    lga_data = lga.get_latest_data(for_display=True, \
        display_options={
            'num_skilled_health_providers_per_1000': {'decimal_places': 3},
            'num_chews_per_1000': {'decimal_places': 3},
            'teacher_nonteachingstaff_ratio_lga': {'decimal_places': 3},
        })
    record_counts = FacilityRecord.counts_by_variable(lga.id)
    def g(slug):
        value_dict = lga_data.get(slug, None)
        if value_dict:
            return value_dict.get('value', None)
        else:
            return None
    def i(slug1, slug2):
        if g(slug1) == None or g(slug2) == None:
            return None
        return "%s/%s" % (g(slug1), g(slug2))
    def h(slug1, slug2):
        try:
            indicator = LGAIndicator.objects.get(slug=slug1)
            count = 0
            records = record_counts[indicator.sector.slug][indicator.origin.slug]
            print records
            for k, v in records.items():
                count += v
        except:
            return None
        return "%s/%s" % (g(slug1), count)
    example = {
        'health': [
            ('Facilities', [
            #proof of concept that lga is accessible from here.
                ["Health Posts and Dispensaries", g("num_level_1_health_facilities"), None, g("target_level_1_health_facilities"), None],
                ["Primary Health Clinics", g("num_level_2_health_facilities"), None, g("target_level_2_health_facilities"), None],
                ["Primary Health Centres", g("num_level_3_health_facilities"), None, g("target_level_3_health_facilities"), None],
                ["Comprehensive Health Centres and Hospitals", g("num_level_4_health_facilities"), None, g("target_level_4_health_facilities"), None],
                ["Other Health Facilities", g("num_level_other_health_facilities"), None, None, None],
                ["Total number of facilities", g("num_health_facilities"), None, g("target_total_health_facilities"), None],
                ["Percentage of facilities that offer inpatient care", g("proportion_health_facilities_inpatient_care"), h("num_health_facilities_inpatient_care", "num_health_facilities"), None, None],
                ["Percentage of facilities that offer care 24 hours a day, 7 days a week", g("proportion_health_facilities_open_24_7"), h("num_health_facilities_open_24_7", "num_health_facilities"), g("target_health_facilities_open_24_7"), g("target_all_but_level_1_health_facilities")],
            ],),
            ('Staffing', [
                ["Total number of doctors in the LGA", g("num_doctors"), None, g("target_num_doctors"), None],
                ["Total number of midwives and nurse-midwives in the LGA", g("num_nursemidwives_midwives"), None, g("target_num_midwives_nursemidwives"), None],
                ["Total number of nurses in the LGA", g("num_nurses"), None, g("target_num_nurses"), None],
                ["Total number of CHEWs (Jr. and Sr.) in the LGA", g("num_chews"), None, g("target_num_chews"), None],
                ["Total number of laboratory technicians in the LGA", g("num_lab_techs"), None, g("target_num_lab_techs"), None],
                ["Number of health providers per 1,000 population", g("num_skilled_health_providers_per_1000"), None, None, None],
                ["Number of CHEWs per 1,000 population", g("num_chews_per_1000"), None, None, None],
                ["Number of facilities where all salaried staff were paid during the last pay period", g("proportion_staff_paid"), h("num_staff_paid", "staff_paid_lastmth_yn"), g("target_total_health_facilities"), "100%"],
            ],),
            ('Child Health', [
                ["Percentage of facilities that offer routine immunization", g("proportion_health_facilities_routine_immunization"), h("num_health_facilities_routine_immunization", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities that offer growth monitoring", g("proportion_growth_monitoring"), h("num_growth_monitoring", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities that offer deworming", g("proportion_deworming"), h("num_deworming", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities that do not charge any fees for child health services", g("proportion_no_user_fees_child_health"), h("num_no_user_fees_child_health", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
            ],),
            ('Maternal Health', [
                ["Percentage of facilities that offer delivery services 24 hours a day, 7 days a week", g("proportion_delivery_24_7"), h("num_delivery_24_7", "num_health_facilities"), g("target_health_facilities_open_24_7"), g("target_all_but_level_1_health_facilities")],
                ["Percentage of facilities with at least one skilled birth attendant", g("proportion_at_least_1_sba"), h("num_at_least_1_sba", "num_health_facilities"), g("target_health_facilities_open_24_7"), g("target_all_but_level_1_health_facilities")],
                ["Percentage of facilities that offer antenatal care", g("proportion_antenatal"), h("num_antenatal", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Number of facilities that perform Caesarean sections", g("num_health_facilities_c_sections"), None, None, None],

                ["Percentage of facilities with access to emergency transport services", g("proportion_access_functional_emergency_transport"), h("num_access_functional_emergency_transport", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities that offer family planning services", g("proportion_family_planning"), h("num_family_planning", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities that do not charge any fees for maternal health services", g("proportion_delivery_no_user_fees"), h("num_delivery_no_user_fees", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
            ],),
            ('HIV/AIDS, Malaria and other Diseases', [
                ["HIV/AIDS"],
                ["Percentage of facilities that offer HIV testing", g("proportion_health_facilities_hiv_testing"), h("num_health_facilities_hiv_testing", "num_health_facilities"), None, None],
                ["Percentage of facilities that offer ART treatment", g("proportion_health_facilities_hiv_testing"), h("num_health_facilities_hiv_testing", "num_health_facilities"), None, None],
                ["Malaria"],
                ["Percentage of facilities that offer malaria testing (RDT or microscopy)", g("proportion_malaria_testing"), h("num_malaria_testing", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities that offer ACT-based treatment for malaria", g("proportion_act_treatment_for_malaria"), h("num_act_treatment_for_malaria", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities that offer malaria prophylaxis during pregnancy", g("proportion_malaria_prevention_pregnancy"), h("num_malaria_prevention_pregnancy", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities that provide bednets", g("proportion_offer_bednets"), h("num_offer_bednets", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities that do not charge and fees for malaria-related services", g("proportion_no_user_fees_malaria"), h("num_no_user_fees_malaria", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Tuberculosis"],
                ["Percentage of facilities that offer TB treatment", g("proportion_health_facilities_hiv_testing"), h("num_health_facilities_hiv_testing", "num_health_facilities"), None, None],
                ["Percentage of facilities that offer TB testing", g("proportion_health_facilities_hiv_testing"), h("num_health_facilities_hiv_testing", "num_health_facilities"), None, None],
            ],),
            ('Infrastructure', [
                ["Percentage of facilities with access to some form of power source", g("proportion_any_power_access"), h("num_any_power_access", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities with access to an improved water source", g("proportion_water_access"), h("num_water_access", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities with functioning improved sanitation", g("proportion_functional_sanitation"), h("num_functional_sanitation", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities with mobile phone coverage somewhere on the premises", g("proportion_mobile_coverage"), h("num_mobile_coverage", "num_health_facilities"), g("target_total_health_facilities"), "100%"],
                ["Percentage of facilities that separate medical waste from other forms of waste", g("proportion_health_facilities_med_waste_separated"), h("num_health_facilities_med_waste_separated", "num_health_facilities"), None, None],
            ],),
            ('Equipment and Supplies', [
                ["Percentage of facilities that experienced a stock-out of essential medications in the past month", g("proportion_stockout_essential_meds"), h("num_stockout_essential_meds", "num_health_facilities"), 0, "0%"],
            ],),
        ],
        'education': [
            ('Facilities', [
                ["Number of primary schools (preprimary, primary, preprimary/primary, primary/js)", g("num_primary_schools"), None, g("target_num_primary_schools")],
                ["Number of junior secondary schools (js, js/ss)", g("num_junior_secondary_schools"), None, g("target_num_junior_secondary_schools")],
                ["Number of senior secondary schools (ss)", g("num_senior_secondary_schools"), None, g("target_num_senior_secondary_schools")],
                ["Total number of schools", g("num_schools"), None, g("target_num_schools")],
            ],),
            ('Access', [
                ["Primary net intake rate (NIR) for boys", "N/A", None, "N/A"],
                ["Primary net intake rate (NIR) for girls", "N/A", None, "N/A"],
                ["Junior secondary net intake rate (NIR) for boys", "N/A", None, "N/A"],
                ["Junior Secondary net intake rate (NIR) for girls", "N/A", None, "N/A"],
                ["Percentage of schools farther than 1km from catchement area", g("proportion_schools_1kmplus_catchment"), h("num_schools_1kmplus_catchment", "num_schools"), "0%", "0"],
                ["Percentage of primary schools farther than 1km from nearest secondary school", g("proportion_primary_schools_1kmplus_ss"), i("num_primary_schools_1kmplus_ss", "num_primary_schools"), "0%", "0"],
                ["Percentage of schools with students living farther than 3km", g("proportion_students_3kmplus"), h("num_students_3kmplus", "students_living_3kmplus_school"), "0%", "0"],
            ],),
            ('Participation', [
                ["Primary net enrollment rate (NER) for boys", g("net_enrollment_rate_boys_primary"), None, "100%"],
                ["Primary net enrollment rate (NER) for girls", g("net_enrollment_rate_girls_primary"), None, "100%"],
                ["Junior secondary net enrollment rate (NER) for boys", g("net_enrollment_rate_boys_js"), None, "100%"],
                ["Junior secondary net enrollment rate (NER) for girls", g("net_enrollment_rate_girls_js"), None, "100%"],
                ["Gender parity index (GPI) for primary schools", g("gender_parity_index_primary"), None, "1", None],
                ["Gender parity index (GPI) for junior secondary schools", g("gender_parity_index_js"), None, "1", None],
            ],),
            ('Infrastructure', [
                ["Water & Santation"],
                ["Percentage of schools with access to potable water", g("proportion_schools_potable_water"), h("num_schools_potable_water", "num_schools"), "100%", g("target_num_schools")],
                ["Percentage of schools with improved sanitation/toilet", g("proportion_schools_improved_sanitation"), h("num_schools_improved_sanitation", "num_schools"), "100%", g("target_num_schools")],
                ["Percentage of schools with gender-separated toilets", g("proportion_schools_gender_sep_toilet"), h("num_schools_gender_sep_toilet", "num_schools"), "100%", g("target_num_schools")],
                ["Pupil to toilet ratio", g("pupil_toilet_ratio"), None, "35"],
                ["Building Structure"],
                ["Percentage of schools with access to power", g("proportion_schools_power_access"), h("num_schools_power_access", "num_schools"), "100%", g("target_num_schools")],
                ["Percentage of classrooms needing major repair", g("proportion_classrooms_need_major_repair"), i("number_classrooms_need_major_repair", "num_classrooms_lga"), "0%", "0"],
                ["Percentage of classrooms needing minor repair", g("proportion_classrooms_need_minor_repair"), i("number_classrooms_need_minor_repair", "num_classrooms_lga"), "0%", "0"],
                ["Percentage of schools with a roof in good condition", g("proportion_schools_covered_roof_good_cond"), h("num_schools_covered_roof_good_cond", "num_schools"), "100%", g("num_schools")],
                ["Health & Safety"],
                ["Percentage of schools with a dispensary/health clinic", g("proportion_schools_with_clinic_dispensary"), h("num_schools_with_clinic_dispensary", "num_schools"), "100%", g("target_num_schools")],
                ["Percentage of schools with a first aid kit only (not a health clinic)", g("proportion_schools_with_first_aid_kit"), h("num_schools_with_first_aid_kit", "num_schools"), "100%", g("target_num_schools")],
                ["Percentage of schools with a wall/fence in good condition", g("proportion_schools_fence_good_cond"), h("num_schools_fence_good_cond", "num_schools"), "100%", g("target_num_schools")],
                ["Learning Environment"],
                ["Pupil to classroom ratio", g("student_classroom_ratio_lga"), None, "35"],
                ["Percentage of schools that teach outside because there are not enough classrooms", g("proportion_schools_hold_classes_outside"), h("num_schools_hold_classes_outside", "num_schools"), "0%", "0"],
                ["Percentage of schools with double shifts", g("proportion_schools_two_shifts"), h("num_schools_two_shifts", "num_schools"), "0%", "0"],
                ["Percentage of schools with multi-grade classrooms", g("proportion_schools_multigrade_classrooms"), h("num_schools_multigrade_classrooms", "num_schools"), "0%", "0"],
            ],),
            ('Furniture', [
                ["Percentage of schools with a chalkboard in every classroom", g("proportion_schools_chalkboard_all_rooms"), h("num_schools_chalkboard_all_rooms", "num_schools"), "100%", g("target_num_schools")],
                ["Pupil to bench ratio", g("pupil_bench_ratio_lga"), None, "&#8804; 3"],
                ["Pupil to desk ratio", g("pupil_desk_ratio_lga"), None, "&#8804; 1"],
            ],),
            ('Adequacy of Staffing', [
                ["Primary school pupil to teacher ratio", g("primary_school_pupil_teachers_ratio_lga"), None, "&#8804; 35"],
                ["Junior secondary school pupil to teacher ratio", g("junior_secondary_school_pupil_teachers_ratio_lga"), None, "&#8804; 35"],
                ["Teaching to non-teaching staff ratio", g("teacher_nonteachingstaff_ratio_lga"), None, "N/A"],
                ["Percentage of qualified teachers (with NCE)", g("proportion_teachers_nce"), i("num_teachers_nce", "num_teachers"), "100%", g("target_num_teachers")],
                ["Percentage of teachers who participated in training in the past 12 months", g("proportion_teachers_training_last_year"), i("num_teachers_training_last_year", "num_teachers"), "100%", g("target_num_teachers")],
	    ],),
	    ('Institutional Development',[
                ["Percentage of schools that have delayed teacher payments in the past 12 months", g("proportion_schools_delay_pay"), h("num_schools_delay_pay", "num_schools"), "0%", "0"],
                ["Percentage of schools that have missed teacher payments in the past 12 months", g("proportion_schools_missed_pay"), h("num_schools_missed_pay", "num_schools"), "0%", "0"],
            ],),
            ('Curriculum Issues', [
                ["Textbook to pupil ratio", g("num_textbooks_per_pupil"), None, "4"],
                ["Percentage of schools where exercise books are provided to students", g("proportion_provide_exercise_books"), h("num_provide_exercise_books", "num_schools"), "100%", g("target_num_schools")],
                ["Percentage of schools where pens/pencils are provided to students", g("proportion_provide_pens_pencils"), h("num_provide_pens_pencils", "num_schools"), "100%", g("target_num_schools")],
                ["Percentage of schools that follow the National UBE Curriculum", g("proportion_natl_curriculum"), h("num_natl_curriculum", "num_schools"), "100%", g("target_num_schools")],
                ["Percentage of schools where each teacher has a teaching guidebook for every subject", g("proportion_teachers_with_teacher_guide"), h("num_teachers_with_teacher_guide", "num_schools"), "100%", g("target_num_schools")],
                ["Percentage of schools with a functioning library", g("proportion_schools_functioning_library"), h("num_schools_functioning_library", "num_schools"), "100%", g("target_num_schools")],
            ],),
            ('Efficiency (flow rates)', [
                ["Drop out rate", "N/A", None, "0%"],
                ["Transition rate (primary to junior secondary) for boys", g("transition_rate_primary_to_js1_male"), None, "100%"],
                ["Transition rate (primary to junior secondary) for girls", g("transition_rate_primary_to_js1_female"), None, "100%"],
                ["Repetition rate (primary) for boys", g("repetition_rate_primary_male"), None, "0%"],
                ["Repetition rate (primary) for girls", g("repetition_rate_primary_female"), None, "0%"],
	    ],),
            ('Learning Outcomes', [
                ["Literacy rate of 15-24 year olds (men and women)", g("literacy_rate"), None, "100%"],
            ],),
        ],
        'water': [
            ('Type', [
                ["Number of boreholes and tube wells", g("num_boreholes_and_tubewells"), None, ""],
                ["Number of developed and treated spring and surface water", g("num_developed_and_treated_or_protected_surface_or_spring_water"), None, ""],
                ["Number of protected dug wells", g("num_protected_dug_wells"), None, ""],
                ["Number of other types of protected water sources", g("num_other_protected_sources"), None, ""],
                ["Number of assessed unprotected water sources", g("num_mapped_unprotected_sources"), None, ""],
                ["Total number of water sources", g("num_water_points"), None, ""],
            ],),
            ('Maintenance', [
                ["Percentage of boreholes, protected or treated sources that are poorly maintained", g("proportion_protected_water_points_non_functional"), i("num_protected_water_sources_non_functional", "num_protected_water_sources"), ""],
            ]),
            ('Population Served', [
                ["Population served per well-maintained borehole, protected or treated water source", g("population_served_per_protected_and_functional_water_source"), None, ""],
                ["Population served per borehole, protected or treated water source (whether or not it is well-maintained)", g("population_served_per_all_water_sources"), None, ""],
            ]),
            ('Lift Mechanisms for Boreholes and Tube Wells', [
                ["Percentage of boreholes and tube wells with a non-motorized lift (human or animal-powered)", g("proportion_boreholes_tubewells_manual"), i("num_boreholes_tubewells_manual", "num_boreholes_and_tubewells"), ""],
                ["Percentage of boreholes and tube wells with a motorized lift", g("proportion_boreholes_tubewells_non_manual"), i("num_boreholes_tubewells_non_manual", "num_boreholes_and_tubewells"), ""],
                ["Percentage of boreholes and tube wells with a diesel lift", g("proportion_boreholes_tubewells_diesel"), i("num_boreholes_tubewells_diesel", "num_boreholes_and_tubewells"), ""],
                ["Percentage of boreholes and tube wells with an electric motor lift", g("proportion_boreholes_tubewells_electric"), i("num_boreholes_tubewells_electric", "num_boreholes_and_tubewells"), ""],
                ["Percentage of boreholes and tube wells with a solar lift", g("proportion_boreholes_tubewells_solar"), i("num_boreholes_tubewells_solar", "num_boreholes_and_tubewells"), ""],
            ],),
            ('Poorly Maintained Lift Mechanisms for Boreholes and Tube Wells', [
                ["Percentage of non-motorized (human or animal-powered) lifts that are poorly maintained", g("proportion_boreholes_tubewells_manual_non_functional"), i("num_boreholes_tubewells_manual_non_functional", "num_boreholes_tubewells_manual"), ""],
                ["Percentage of all motorized lifts that are poorly maintained", g("proportion_boreholes_tubewells_non_manual_non_functional"), i("num_boreholes_tubewells_non_manual_non_functional", "num_boreholes_tubewells_non_manual"), ""],
                ["Percentage of diesel-powered lifts that are poorly maintained", g("proportion_boreholes_tubewells_diesel_non_functional"), i("num_boreholes_tubewells_diesel_non_functional", "num_boreholes_tubewells_diesel"), ""],
                ["Percentage of electrically-powered lifts that are poorly maintained", g("proportion_boreholes_tubewells_electric_non_functional"), i("num_boreholes_tubewells_electric_non_functional", "num_boreholes_tubewells_electric"), ""],
                ["Percentage of solar-powered lifts that are poorly maintained", g("proportion_boreholes_tubewells_solar_non_functional"), i("num_boreholes_tubewells_solar_non_functional", "num_boreholes_tubewells_solar"), ""],
            ]),
        ],
    }
    return example.pop(sector_slug, [])

def new_sector_overview(request, lga_id, sector_slug):
    try:
        lga = LGA.objects.get(unique_slug=lga_id)
    except:
        return HttpResponseRedirect("/new_dashboard/")
    if sector_slug not in ["education", "health", "water"]:
        return HttpResponseRedirect("/new_dashboard/")
    sector_name = sector_slug.capitalize()
    context = RequestContext(request)
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
    context.navs = [{ 'url': '/', 'name': 'Home' },
                    { 'url': '/new_dashboard/%s' % lga.unique_slug, 'name': lga.name },
                    { 'url': '/new_dashboard/%s/%s' % (lga.unique_slug, sector_slug),
                        'name': sector_slug.capitalize(),
                        'active': True }]
    #tmp deactivating breadcrumb
    context.navs = False
    context.table_data = tmp_variables_for_sector(sector_slug, lga)
    context.sector = sector_slug
    return render_to_response("new_sector_overview.html", context_instance=context)
