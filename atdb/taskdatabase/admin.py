from django.contrib import admin
from .models import Location, Status, DataProduct, Observation

admin.site.register(Location)
admin.site.register(Status)
admin.site.register(DataProduct)
admin.site.register(Observation)