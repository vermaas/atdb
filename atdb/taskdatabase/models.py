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

class Location(models.Model):
    location = models.CharField(max_length=255, default="unknown",blank=True, null=True)
    timestamp = models.DateTimeField('Timestamp of creation in the database.', default=datetime.now, blank=True)

    def __str__(self):
         return str(self.location)


class StatusType(models.Model):

    STATUS_TYPE_OBJECT_CHOICES = (('observation','observation'),('dataproduct','dataproduct'))

    name = models.CharField(max_length=20, choices=STATUS_TYPE_NAME_CHOICES, default="unknown")
    object = models.CharField(max_length=20, choices=STATUS_TYPE_OBJECT_CHOICES, default="dataproduct")

    def __str__(self):
         return str(self.id)+':'+str(self.object + '.' +self.name)


class Status(models.Model):
    statusType = models.ForeignKey(StatusType, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField('Timestamp of creation in the database.', default=datetime.now, blank=True)

    def __str__(self):
        return str(self.id)+' - '+str(self.derived_name)+' ('+str(self.derived_object)+')'

    @property
    def derived_name(self):
        return self.statusType.name

    @property
    def derived_object(self):
        return self.statusType.object


class TaskObject(models.Model):
    TASK_TYPE__CHOICES = (
        (TASK_TYPE_OBSERVATION, TASK_TYPE_OBSERVATION),
        (TASK_TYPE_DATAPRODUCT, TASK_TYPE_DATAPRODUCT)
    )
    name = models.CharField(max_length=100, default="unknown")
    task_type = models.CharField(max_length=20, choices=TASK_TYPE__CHOICES, default=TASK_TYPE_DATAPRODUCT)

    taskID = models.CharField('runId', max_length=30, blank=True, null=True)
    creationTime = models.DateTimeField(default=datetime.now, blank=True)

    new_status = models.CharField(max_length=20,choices=STATUS_TYPE_NAME_CHOICES, default="defined")
    new_location = models.CharField(max_length=255, default="unknown",null=True)
    # locations = models.ForeignKey(Location, null=True, blank=True, on_delete=models.CASCADE)
    locations = models.ManyToManyField(Location, null=True, blank=True)
    status = models.ForeignKey(Status, related_name='taskobject_status', null=True, on_delete=models.CASCADE)
    statusHistory = models.ManyToManyField(Status, related_name='dataproduct_status_history', blank=True)


    def __str__(self):
        return str(self.id)

    @property
    def derived_status(self):
        try:
            return self.status.statusType.name
        except:
            return None

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

