from time import sleep
from celery import shared_task


@shared_task
def notify_customers(message):
    print('Sending 10k emails')
    print(message)
    sleep(10)
    print('EMail were sent') 