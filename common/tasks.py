from allauth.utils import get_user_model
from celery import shared_task
from celery.utils.log import get_task_logger

log = get_task_logger(__name__)

@shared_task(ignore_result=True)
def cleanup_accounts(user_id=None):
    User = get_user_model()
    abandoned_users = User.objects.filter(emailaddress__primary=True, emailaddress__verified=False)
    log.info("Deleting {0} abandoned users".format(abandoned_users.count()))
    abandoned_users.delete()
