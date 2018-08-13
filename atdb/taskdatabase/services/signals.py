import logging;

from django.db.models.signals import pre_save, post_save
from django.core.signals import request_started, request_finished
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from taskdatabase.models import TaskObject, Observation, DataProduct, Location, Status, StatusType
from . import jobs

"""
Signals sent from different parts of the backend are centrally defined and handled here.
"""

logger = logging.getLogger(__name__)


#--- HTTP REQUEST signals-------------

@receiver(request_started)
def request_started_handler(sender, **kwargs):
    logger.debug("signal : request_started")


@receiver(request_finished)
def request_finished_handler(sender, **kwargs):
    logger.debug("signal : request_finished")

#--- Observation and DataProduct signals-------------

@receiver(pre_save, sender=Observation)
def pre_save_observation_handler(sender, **kwargs):
    logger.info("SIGNAL : pre_save Observation(" + str(kwargs.get('instance')) + ")")
    handle_pre_save(sender, **kwargs)

@receiver(pre_save, sender=DataProduct)
def pre_save_dataproduct_handler(sender, **kwargs):
    logger.info("SIGNAL : pre_save DataProduct(" + str(kwargs.get('instance')) + ")")
    handle_pre_save(sender, **kwargs)


def handle_pre_save(sender, **kwargs):
    """
    pre_save handler for both Observation and Dataproduct. Mainly to check status changes and dispatch jobs in needed.
    :param (in) sender: The model class that sends the trigger
    :param (in) kwargs: The instance of the object that sends the trigger.
    """
    logger.info("handle_pre_save(" + str(kwargs.get('instance')) + ")")
    myTaskObject = kwargs.get('instance')

    # IF this object does not exist yet, then abort, and let it first be handled by handle_post_save (get get a id).
    if myTaskObject.id==None:
        return None

    current_status = str(myTaskObject.derived_status)
    new_status = str(myTaskObject.new_status)
    new_location = str(myTaskObject.new_location)
    logger.info("*** new_location = " + str(new_location) + ")")

    # handle location change
    if (new_location!='None'):
        # add a new location to myTaskObject
        logger.info("*** adding New Location = " + str(new_location))
        myLocation = Location(location=myTaskObject.new_location)
        myLocation.save()
        myTaskObject.locations.add(myLocation)

    # handle status change
    if (new_status!=None) and (current_status!=new_status):
        # add the current status object to the status history.
        myTaskObject.statusHistory.add(myTaskObject.status)

        # then create a new status object and add it to myTaskObject
        myStatusType = StatusType.objects.get(name=new_status, object=myTaskObject.task_type)
        myStatus = Status(statusType=myStatusType)
        myStatus.save()
        myTaskObject.status = myStatus

    # temporarily disconnect the post_save handler to save the dataproduct (again) and avoiding recursion.
    # I don't use pre_save, because then the 'created' key is not available, which is the most handy way to
    # determine if this dataproduct already exists. (I could also check the database, but this is easier).
    disconnect_signals()
    myTaskObject.save()
    connect_signals()

    # dispatch a job if the status has changed.
    if (new_status != None) and (current_status != new_status):
        jobs.dispatchJob(myTaskObject, new_status)


@receiver(post_save, sender=Observation)
def post_save_observation_handler(sender, **kwargs):
    logger.info("SIGNAL : post_save Observation(" + str(kwargs.get('instance')) + ")")
    handle_post_save(sender, **kwargs)


@receiver(post_save, sender=DataProduct)
def post_save_dataproduct_handler(sender, **kwargs):
    logger.info("SIGNAL : post_save DataProduct(" + str(kwargs.get('instance')) + ")")
    handle_post_save(sender, **kwargs)


def handle_post_save(sender, **kwargs):
    """
     pre_save handler for both Observation and Dataproduct. To create and write its initial status and location
    :param (in) sender: The model class that sends the trigger
    :param (in) kwargs: The instance of the object that sends the trigger.
    """
    logger.info("handle_post_save("+str(kwargs.get('instance'))+")")
    myTaskObject = kwargs.get('instance')

    # if this is a new dataproduct, then first create a new status and a new locaton for it
    if kwargs['created']:
        logger.info("save new "+str(myTaskObject.task_type))

        # create new location, use as default the 'current_location' that is provided in the http request
        myLocation = Location(location=myTaskObject.new_location)
        myLocation.save()
        myTaskObject.locations.add(myLocation)
        # myTaskObject.locations_set.add(myLocation)

        # set status
        myStatusType = StatusType.objects.get(name=myTaskObject.new_status, object=myTaskObject.task_type)
        myStatus = Status(statusType=myStatusType)
        myStatus.save()
        myTaskObject.status = myStatus

        # if there already is an observation with this taskID, then add this dataproduct to it.
        # TODO

        # temporarily disconnect the post_save handler to save the dataproduct (again) and avoiding recursion.
        # I don't use pre_save, because then the 'created' key is not available, which is the most handy way to
        # determine if this dataproduct already exists. (I could also check the database, but this is easier).
        disconnect_signals()
        myTaskObject.save()
        connect_signals()


def connect_signals():
    logger.info("connect_signals")
    pre_save.connect(pre_save_observation_handler, sender=Observation)
    pre_save.connect(pre_save_dataproduct_handler, sender=DataProduct)
    post_save.connect(post_save_observation_handler, sender=Observation)
    post_save.connect(post_save_dataproduct_handler, sender=DataProduct)


def disconnect_signals():
    logger.info("disconnect_signals")
    pre_save.disconnect(pre_save_observation_handler, sender=Observation)
    pre_save.disconnect(pre_save_dataproduct_handler, sender=DataProduct)
    post_save.disconnect(post_save_observation_handler, sender=Observation)
    post_save.disconnect(post_save_dataproduct_handler, sender=DataProduct)