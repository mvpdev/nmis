# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from parsed_xforms.models import InstanceModification
from xform_manager.models import Instance
from django.http import HttpResponse

def hide_instance_field(request, instance_id, field_slug):
    user = request.user
    i = Instance.objects.get(id=instance_id)
    action = "delete"
    xpath = field_slug
    InstanceModificiation.objects.get_or_create(user=user,
            instance=i, action='delete',
            xpath=field_slug)
    i.parsed_instance.save()
    return HttpResponse("OK")