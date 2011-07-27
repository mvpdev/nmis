#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from xform_manager.models import Instance, XForm
from parsed_xforms.models import ParsedInstance, Registration
from nga_districts import models as nga_models
from surveyor_manager.models import Surveyor
from queryset_iterator import queryset_iterator

from django.contrib.auth.models import User
from django.conf import settings

import time
import math
import gc

xform_db = settings.MONGO_DB
xform_instances = xform_db.instances


def delete_all_parsed_instances():
    # ParsedInstance.objects.all().delete()
    # Ends up blowing memory, so I need to iterate through all the
    # parsed instances and delete them.
    while ParsedInstance.objects.count() > 0:
        for pi in ParsedInstance.objects.all()[0:1000]:
            pi.delete()


def get_counts():
    cols = ['instances', 'parsed_instances', 'mongo_instances', \
            'districts_assigned', 'districts_total', 'registrations', \
            'surveyors', 'users'] 
    counts = {
        'instances': Instance.objects.count(),
        'parsed_instances': ParsedInstance.objects.count(),
        'districts_assigned': ParsedInstance.objects.exclude(lga=None).count(),
        'districts_total': nga_models.LGA.objects.count(),
        'registrations': Registration.objects.count(),
        'mongo_instances': xform_instances.count(),
        'surveyors': Surveyor.objects.count(),
        'users': User.objects.count()
    }
    return (cols, counts, time.clock())


def print_counts(func):
    def wrapper(*args, **kwargs):
        cols, counts_1, start_time = get_counts()
        result = func(*args, **kwargs)
        cols, counts_2, end_time = get_counts()
        print "That process took [%d ticks]" % math.floor(1000 * (end_time-start_time))
        display_counts_as_table(cols, [counts_1, counts_2])
        return result
    return wrapper


@print_counts
def reparse_all():
    print "[Reparsing XForm Instances]\n"

    for i in queryset_iterator(Instance.objects.all()):
        try:
            i.save()
        except Exception as e:
            # There are a few instances that throw errors
            print e


def display_counts_as_table(cols, list_of_dicts):
    strs = [[] for row in list_of_dicts]
    col_heads = []
    breaker = []
    for c in cols:
        col_heads.append(" %-19s" % c)
        breaker.append("--------------------")
        for i in range(0, len(list_of_dicts)):
            strs[i].append(" %-18d " % list_of_dicts[i][c])
    
    print '|'.join(col_heads)
    print '-'.join(breaker)
    for starr in strs:
        print '|'.join(starr)
