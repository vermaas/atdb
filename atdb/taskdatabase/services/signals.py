import logging;

from django.db.models.signals import pre_save, post_save
from django.core.signals import request_started, request_finished
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from taskdatabase.models import Observation, DataProduct, Location, Status, StatusType

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

#--- DataProduct signals-------------

@receiver(pre_save, sender=DataProduct)
def pre_save_dataproduct_handler(sender, **kwargs):
    """
    intercept the object before it is saved. To check if a status change is requested
    :param (in) sender: The model class that sends the trigger
    :param (in) kwargs: The instance of the object that sends the trigger.
    """
    logger.info("SIGNAL : pre_save_dataproduct_handler(" + str(kwargs.get('instance')) + ")")
    myDataProduct = kwargs.get('instance')
    current_status = str(myDataProduct.derived_status)
    logger.info('current_status = '+current_status)
    new_status = myDataProduct.new_status
    logger.info('new_status = ' + new_status)

    if (new_status!=None) and (current_status!=new_status):
        logger.info('status change detected: ' + current_status + ' => ' + new_status + ' for ' + myDataProduct.filename)
        dispatchJob(myDataProduct,new_status)


@receiver(post_save, sender=DataProduct)
def post_save_dataproduct_handler(sender, **kwargs):
    """
    intercept the dataproduct 'save' operation to write its initial status and location
    :param (in) sender: The model class that sends the trigger
    :param (in) kwargs: The instance of the object that sends the trigger.
    """
    logger.info("SIGNAL : post_save_dataproduct_handler("+str(kwargs.get('instance'))+")")
    myDataProduct = kwargs.get('instance')

    # if this is a new dataproduct, then first create a new status and a new locaton for it
    if kwargs['created']:
        logger.info("save new dataproduct")

        # create new location, use as default the 'current_location' that is provided in the http request
        myLocation = Location(location=myDataProduct.new_location)
        myLocation.save()

        # set default status 'defined'
        myStatusType = StatusType.objects.get(name=myDataProduct.new_status, object='dataproduct')
        myStatus = Status(statusType=myStatusType)

        # this save will trigger a signal that a status has changed...
        myStatus.save()

        myDataProduct.locations.add(myLocation)
        myDataProduct.status = myStatus

        # if there already is an observation with this taskID, then add this dataproduct to it.
        # TODO

        # temporarily disconnect the post_save handler to save the dataproduct (again) and avoiding recursion.
        # I don't use pre_save, because then the 'created' key is not available, which is the most handy way to
        # determine if this dataproduct already exists. (I could also check the database, but this is easier).
        post_save.disconnect(post_save_dataproduct_handler, sender=sender)
        myDataProduct.save()
        post_save.connect(post_save_dataproduct_handler, sender=sender)



def dispatchJob(myObject, status):
    logger.info("*** dispatchJob(" + str(myObject) + "," + str(status) + ") ***")
