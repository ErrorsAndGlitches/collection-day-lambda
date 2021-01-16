from datetime import datetime
from pytz import timezone
from os import environ
import boto3

from cdl.collection_calendar import CollectionCalendar
from cdl.notifications import SnsNotification


def collection_day_lambda_handler(event, context):
    send_collection_day_notification(
        SnsNotification(boto3.client('sns'), environ['PHONE_NUMBERS'].split(',')),
        environ['ADDRESS']
    )
    return {
        'result': 'success'
    }


def send_collection_day_notification(notifications, address):
    today_date = datetime.now(tz=timezone('America/Los_Angeles')).date()
    notifications.send(str(CollectionCalendar(address, today_date).next_collection_msg()))
