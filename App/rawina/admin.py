from django.contrib import admin
from rawina.models import Story

# Register your models here.
admin.site.register(Story)

admin.site.site_header = "Rawina Admin"
admin.site.site_title = "Rawina Admin Portal"
admin.site.index_title = "Welcome to the Rawina Admin Portal"