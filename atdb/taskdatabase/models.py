from django.db import models
from django.utils.timezone import datetime

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

STATUS_UNKNOWN = 'unknown'
STATUS_DEFINED = 'defined'
STATUS_CREATED = 'created'
STATUS_VALID = 'valid'
STATUS_COPIED = 'copied'
STATUS_ARCHIVED = 'archived'
STATUS_SECURED = 'secured'
STATUS_REMOVED = 'removed'


class Location(models.Model):
    host = models.CharField(max_length=100, default="unknown")
    path = models.CharField(max_length=255, default="unknown")
    timestamp = models.DateTimeField('Timestamp of creation in the database.', default=datetime.now, blank=True)

    def __str__(self):
         return str(self.host + self.path)


class StatusType(models.Model):

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
    name = models.CharField(max_length=20, choices=DATAPRODUCT_STATUS_CHOICES, default="unknown")
    object = models.CharField(max_length=20, choices=DATAPRODUCT_STATUS_CHOICES, default="dataproduct")

    def __str__(self):
         return str(self.object + '.' +self.name)

class DataProductStatus(models.Model):

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

class Status(models.Model):
    statusType = models.ForeignKey(StatusType, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField('Timestamp of creation in the database.', default=datetime.now, blank=True)

    def __str__(self):
        return str(self.statusType)


class DataProduct(models.Model):

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

    filename = models.CharField(max_length=200, default="unknown")
    description = models.CharField(max_length=255, default="unknown")
    type = models.CharField('type', choices=DATAPRODUCT_TYPE_CHOICES, default=TYPE_VISIBILITY, max_length=50)
    taskID = models.CharField('runId', max_length=30, unique=True)

    creationTime = models.DateTimeField(default=datetime.now, blank=True)
    size = models.BigIntegerField(default=0)
    quality = models.CharField(max_length=30, default="unknown")

    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    status = models.ForeignKey(Status, null=True, on_delete=models.SET_NULL)
    statusHistory = models.ForeignKey(Status, related_name='dataproduct_status_history', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.filename


class Observation(models.Model):

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

    name = models.CharField(max_length=100, default="unknown")
    process_type = models.CharField(max_length=50, default="observation")
    taskID = models.CharField('runId', max_length=30, unique=True)

    creationTime = models.DateTimeField(default=datetime.now, blank=True)

    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    status = models.ForeignKey(Status, null=True, on_delete=models.SET_NULL)
    statusHistory = models.ForeignKey(Status, related_name='observation_status_history', null=True, on_delete=models.SET_NULL)
    generatedDataProducts = models.ManyToManyField(DataProduct, related_name='generatedByObservation', blank=True)

    def __str__(self):
        return str(self.taskID + ' - ' +self.name)
