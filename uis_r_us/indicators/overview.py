import json
import re
import os
from django.conf import settings
from facilities.models import LGAIndicator


def read_overview_sectors_json():
    with open(os.path.join(settings.PROJECT_ROOT, 'uis_r_us', 'indicators', 'overview.json'), 'r') as ff:
        ex_json = ff.read()
        ex_obj = json.loads(ex_json)
    return ex_obj

def tmp_variables_for_sector(sector_slug, lga_data, record_counts):
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
            for k, v in records.items():
                count += v
        except:
            return None
        return "%s/%s" % (g(slug1), count)

    ex_obj = read_overview_sectors_json()

    def unpack_section(s):
        def pluck_g_or_h(val):
            g_match = re.match("^g::(.*)$", val)
            if g_match:
                return g(g_match.groups()[0])
            h_match = re.match("^h::(.*)$", val)
            if h_match:
                h_args = h_match.groups()[0].split(",")
                return h(*h_args)
            gfrac_match = re.match("^g_fraction::(.*)$", val)
            if gfrac_match:
                gf_args = gfrac_match.groups()[0].split(",")
                return i(*gf_args)
            return val
        def unpack_cell(key, val):
            if isinstance(val, basestring):
                val = pluck_g_or_h(val)
            return (key, val)
        def unpack_row(r):
            return dict([unpack_cell(key, val) for key, val in r.items()])
        def unpack_rows(subsector, ssrows):
            return (subsector, [unpack_row(row) for row in ssrows])
        return [unpack_rows(ss, ssr) for ss, ssr in s]
    for sector in ex_obj:
        sector_d = ex_obj[sector]
        ex_obj[sector] = unpack_section(sector_d)
    return ex_obj.pop(sector_slug, [])
