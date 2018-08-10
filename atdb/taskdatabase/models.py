from django.db import models
from django.utils.timezone import datetime

class Location(models.Model):
    host = models.CharField(max_length=100, default="unknown")
    path = models.CharField(max_length=255, default="unknown")
    timestamp = models.DateTimeField('Timestamp of creation in the database.', default=datetime.now, blank=True)

    def __str__(self):
         return str(self.host + self.path)


class DataProductStatus(models.Model):
    STATUS_UNKNOWN = 'unknown'
    STATUS_DEFINED = 'defined'
    STATUS_CREATED = 'created'
    STATUS_VALID = 'valid'
    STATUS_COPIED = 'copied'
    STATUS_ARCHIVED = 'archived'
    STATUS_SECURED = 'secured'
    STATUS_REMOVED = 'removed'

    DATAPRODUCT_STATUS_CHOICES = (
        (STATUS_UNKNOWN, 'unknown'),
        (STATUS_DEFINED, 'defined'),
        (STATUS_CREATED, 'created'),
        (STATUS_VALID, 'valid'),
        (STATUS_COPIED, 'copied'),
        (STATUS_ARCHIVED, 'archived'),
        (STATUS_SECURED, 'secured'),
        (STATUS_REMOVED, 'removed'),
    )
    status = models.CharField(max_length=20, choices=DATAPRODUCT_STATUS_CHOICES, default="unknown")
    timestamp = models.DateTimeField('Timestamp of creation in the database.', default=datetime.now, blank=True)

    def __str__(self):
        return self.status


class DataProduct(models.Model):
    # constants
    TYPE_IMAGE = 'image'
    TYPE_CUBE = 'cube'
    TYPE_PHOTOMETRY = 'photometry'
    TYPE_SPECTRUM = 'spectrum'
    TYPE_SED = 'sed'
    TYPE_TIMESERIES = 'timeSeries'
    TYPE_VISIBILITY = 'visibility'
    TYPE_EVENT = 'event'
    TYPE_CATALOG = 'catalog'
    TYPE_INSPECTIONPLOT = 'inspectionPlot'

    DATAPRODUCT_TYPE_CHOICES = (
        (TYPE_IMAGE, 'image'),
        (TYPE_CUBE, 'cube'),
        (TYPE_PHOTOMETRY, 'photometry'),
        (TYPE_SPECTRUM, 'spectrum'),
        (TYPE_SED, 'sed'),
        (TYPE_TIMESERIES, 'timeseries'),
        (TYPE_VISIBILITY, 'visibility'),
        (TYPE_EVENT, 'event'),
        (TYPE_CATALOG, 'catalog'),
        (TYPE_INSPECTIONPLOT, 'inspectionPlot'),
    )

    name = models.CharField(max_length=200, default="unknown")
    type = models.CharField('type', choices=DATAPRODUCT_TYPE_CHOICES, default=TYPE_VISIBILITY, max_length=50)
    taskId = models.CharField('runId', max_length=30, unique=True)

    creationTime = models.DateTimeField('Timestamp of creation in the database.', default=datetime.now, blank=True)
    size = models.BigIntegerField(default=0)
    quality = models.CharField(max_length=30, default="unknown")

    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    actual_state = models.ForeignKey(DataProductStatus, null=True, on_delete=models.SET_NULL)
    state_history = models.ForeignKey(DataProductStatus, related_name='state_history', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
