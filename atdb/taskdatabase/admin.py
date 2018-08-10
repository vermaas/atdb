from django.contrib import admin
from .models import Location, Status, StatusType, DataProduct, Observation

admin.site.register(Location)
admin.site.register(Status)
admin.site.register(StatusType)
admin.site.register(DataProduct)
admin.site.register(Observation)