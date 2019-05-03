import boto3
from os import environ
from datetime import datetime
from pytz import timezone

from cdl.collection_calendar import CollectionCalendar


def collection_day_lambda_handler(event, context):
    send_collection_day_notification(
        boto3.client('sns'),
        environ['ADDRESS'],
        environ['PHONE_NUMBERS'].split(',')
    )

    return {
        'result': 'success'
    }


def send_collection_day_notification(sns_client, address, phone_numbers):
    today_date = datetime.now(tz=timezone('America/Los_Angeles')).date()
    msg = str(CollectionCalendar(address, today_date).next_collection())

    for phone_number in phone_numbers:
        sns_client.publish(
            PhoneNumber=phone_number,
            Message=msg
        )
