from unittest import TestCase
from unittest.mock import Mock
from datetime import datetime

from sbp.sbp_email import SbpEmail
from sbp.sbp_response import TimeEntry


class TestSbpEmail(TestCase):
    def test_email_body(self):
        ses_mock = Mock()
        SbpEmail(
            [TimeEntry(datetime(2020, 11, 5, 7, 30), datetime(2020, 11, 5, 9, 0), 2)],
            'from-email@gmail.com',
            'to-email@gmail.com',
            ses_mock
        ).send()

        ses_mock.send_email.assert_called_with(
            Source='from-email@gmail.com',
            Destination={
                'ToAddresses': ['to-email@gmail.com'],
                'CcAddresses': [],
                'BccAddresses': []
            },
            Message={
                'Subject': {
                    'Data': 'Opening SBP fitness slots exist!'
                },
                'Body': {
                    'Html': {
                        'Data': '<a href="https://seattleboulderingproject.com/reserve-fitness">reserve fitness page</a><br/><br/><ol><li>[07:30 - 09:00]: 2</li></ol>'
                    }
                }
            },
        )
