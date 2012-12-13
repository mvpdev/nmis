# Create your views here.
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext
import json

from nga_districts.models import LGA
from facilities.models import Facility, FacilityRecord, Variable


def home(request):
    context = RequestContext(request)
    context.sites = LGA.objects.all()
    return render_to_response("list_lgas.html", context_instance=context)


def data_dictionary(request):
    return HttpResponse(Variable.get_full_data_dictionary())

def facilities_for_site(request, site_id):
    try:
        lga = LGA.objects.get(unique_slug=site_id)
    except LGA.DoesNotExist, e:
        return HttpResponseServerError("Site with ID: %s not found" % site_id)
    d = facilities_dict_for_site(lga)
    return HttpResponse(json.dumps(d))

def facilities_dict_for_site(site):
    def non_null_value(t):
        # returns the first non-null value
        for val_k in ['string_value', 'float_value', 'boolean_value']:
            if t[val_k] is not None:
                return t[val_k]
        return None
    oput = {
        'lgaName': lga.name,
        'stateName': lga.state.name,
    }
    if not lga.data_available:
        oput['error'] = "I'm sorry, it appears data is not available for this LGA at this moment."
    elif not lga.data_loaded:
        oput['error'] = "Data for this LGA is temporarily unavailable. Please check back shortly."
    else:
        d = {}
        drq = FacilityRecord.objects.order_by('-date')
        for facility_dict in Facility.objects.filter(lga=lga).values('id'):
            facility = facility_dict['id']
            drs = drq.filter(facility=facility)
            dvals = {}
            for t in drs.values('variable_id', 'string_value', 'float_value', 'boolean_value', 'date'):
                vid = t['variable_id']
                if vid not in dvals or dvals[vid][0] < t['date']:
                    dvals[vid] = \
                            (t['date'], non_null_value(t))
            dvoput = {}
            for variable in dvals.keys():
                dvoput[variable] = dvals[variable][1]
            if u'photo' in dvoput and u's3_photo_id' not in dvoput:
                fobj = Facility.objects.get(id=facility)
                dvoput[u's3_photo_id'] = fobj.save_s3_photo_id()
            d[facility] = dvoput
        oput['facilities'] = d
        oput['profileData'] = lga.get_latest_data()
    return oput

def facility(request, facility_id):
    """
    Return the latest information we have on this facility.
    """
    facility = Facility.objects.get(id=facility_id)
    text = json.dumps(facility.get_latest_data(), indent=4, sort_keys=True)
    return HttpResponse(text)


def boolean_counts_for_facilities_in_lga(request, lga_id):
    lga = LGA.objects.get(id=lga_id)
    text = json.dumps(FacilityRecord.counts_of_boolean_variables(lga), indent=4, sort_keys=True)
    return HttpResponse(text)
