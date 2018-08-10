from django.contrib import admin
from .models import Location, DataProductStatus, DataProduct

admin.site.register(Location)
admin.site.register(DataProductStatus)
admin.site.register(DataProduct)