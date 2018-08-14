from django.db import models
from django.utils.timezone import datetime

# constants
TASK_TYPE_OBSERVATION = 'observation'
TASK_TYPE_DATAPRODUCT = 'dataproduct'

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

STATUS_TYPE_NAME_CHOICES = (
    (STATUS_UNKNOWN, 'unknown'),
    (STATUS_DEFINED, 'defined'),
    (STATUS_CREATED, 'created'),
    (STATUS_VALID, 'valid'),
    (STATUS_COPIED, 'copied'),
    (STATUS_ARCHIVED, 'archived'),
    (STATUS_SECURED, 'secured'),
    (STATUS_REMOVED, 'removed'))

TASK_TYPE__CHOICES = (
    (TASK_TYPE_OBSERVATION, TASK_TYPE_OBSERVATION),
    (TASK_TYPE_DATAPRODUCT, TASK_TYPE_DATAPRODUCT)
)

class Location(models.Model):
    location = models.CharField(max_length=255, default="unknown",blank=True, null=True)
    timestamp = models.DateTimeField('Timestamp of creation in the database.', default=datetime.now, blank=True)

    def __str__(self):
         return str(self.location)


class Status(models.Model):
#    name = models.CharField(max_length=20, choices=STATUS_TYPE_NAME_CHOICES, default="unknown")
    name = models.CharField(max_length=20, default="unknown")
    timestamp = models.DateTimeField('Timestamp of creation in the database.', default=datetime.now, blank=True)

    def __str__(self):
        return str(self.name)


class TaskObject(models.Model):
    name = models.CharField(max_length=100, default="unknown")
    task_type = models.CharField(max_length=20, choices=TASK_TYPE__CHOICES, default=TASK_TYPE_DATAPRODUCT)

    taskID = models.CharField('runId', max_length=30, blank=True, null=True)
    creationTime = models.DateTimeField(default=datetime.now, blank=True)

#    new_status = models.CharField(max_length=20,choices=STATUS_TYPE_NAME_CHOICES, default="defined")
    new_status = models.CharField(max_length=20, default="defined", null=True)

    new_location = models.CharField(max_length=255, default="unknown",null=True)
    # locations = models.ForeignKey(Location, null=True, blank=True, on_delete=models.CASCADE)
    locations = models.ManyToManyField(Location, null=True, blank=True)
    my_locations = models.CharField(max_length=1024, default="")

    # my_status is 'platgeslagen', because django-filters can not filter on a related property,
    # and I need services to be able to filter on a status to execute their tasks.
    my_status = models.CharField(max_length=20,default="defined")
    statusHistory = models.ManyToManyField(Status, related_name='status_history', blank=True)

    def __str__(self):
        return str(self.id)


class DataProduct(TaskObject):

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
    dataproduct_type = models.CharField('type', choices=DATAPRODUCT_TYPE_CHOICES, default=TYPE_VISIBILITY, max_length=50)

    size = models.BigIntegerField(default=0)
    quality = models.CharField(max_length=30, default="unknown")

    def __str__(self):
        return self.filename



class Observation(TaskObject):

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

    process_type = models.CharField(max_length=50, default="observation")
    generatedDataProducts = models.ManyToManyField(DataProduct, related_name='generatedByObservation', blank=True)

    def __str__(self):
        return str(self.taskID + ' - ' +self.name)

