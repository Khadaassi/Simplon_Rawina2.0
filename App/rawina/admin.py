from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from rawina.models import Story

admin.site.register(Story)

admin.site.site_header = _("Rawina Admin")
admin.site.site_title = _("Rawina Admin Portal")
admin.site.index_title = _("Welcome to the Rawina Admin Portal")
