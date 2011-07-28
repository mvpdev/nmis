#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 coding=utf-8

from django.core.management.base import BaseCommand
from parsed_xforms import reparse

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        command = args[0]
        args = args[1:]
        if hasattr(reparse, command):
            function = getattr(reparse, command)
            function(*args)
