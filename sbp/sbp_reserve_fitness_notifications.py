#!/usr/bin/env python3

from os import environ
from datetime import datetime

import boto3

from sbp.sbp_email import SbpEmail
from sbp.sbp_request import SbpRequest
from sbp.sbp_response import TimeFilter, OpeningsFilter

SHOW_DATE_ENV_KEY = 'SHOW_DATE'
START_TIME_ENV_KEY = 'START_TIME'
END_TIME_ENV_KEY = 'END_TIME'
FROM_EMAIL_ENV_KEY = 'FROM_EMAIL'
TO_EMAIL_ENV_KEY = 'TO_EMAIL'
RESERVATION_TYPE_KEY = 'RESERVATION_TYPE'


def sbp_lambda_handler(event, context):
    check_fitness_reservations_for_openings(
        environ[SHOW_DATE_ENV_KEY],
        environ[START_TIME_ENV_KEY],
        environ[END_TIME_ENV_KEY],
        environ[FROM_EMAIL_ENV_KEY],
        environ[TO_EMAIL_ENV_KEY],
        environ[RESERVATION_TYPE_KEY],
        boto3.client('ses')
    )

    return {
        'result': 'success'
    }


def check_fitness_reservations_for_openings(date, start_time_s, end_time_s, from_email, to_email, reservation_type, ses):
    start_time = datetime.strptime(start_time_s, '%H:%M')
    end_time = datetime.strptime(end_time_s, '%H:%M')

    entries = OpeningsFilter(TimeFilter(
        SbpRequest(date, reservation_type).response(), start_time, end_time
    )).time_entries()

    if len(entries) > 0:
        print('Found opening')
        for entry in entries:
            print(entry)
        SbpEmail(entries, from_email, to_email, ses).send()
    else:
        print('Found no openings')
