import logging, pdb;

from django.db.models.signals import pre_save, post_save
from django.core.signals import request_started, request_finished
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType


from taskdatabase.models import Observation, DataProduct

from rest_framework.authtoken.models import Token

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

@receiver(post_save, sender=DataProduct)
def post_save_dataproduct_handler(sender, **kwargs):
    """
    intercept the dataproduct 'save' operation to write its initial status and location
    :param (in) sender: The model class that sends the trigger
    :param (in) kwargs: The instance of the object that sends the trigger.
    """
    logger.info("SIGNAL : post_save_dataproduct_handler("+str(kwargs.get('instance'))+")")
    myDataProduct = kwargs.get('instance')

