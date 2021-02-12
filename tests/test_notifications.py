from unittest import TestCase
from unittest.mock import Mock, call

from cdl.notifications import SnsNotification, StdoutNotification


class TestCollectionInfo(TestCase):
    _MSG_ATTRIBUTES = {
        'AWS.SNS.SMS.SMSType': {
            'DataType': 'String',
            'StringValue': 'Transactional'
        }
    }

    def test_sns_notification(self):
        sns = Mock()
        phone_numbers = [
            '+00000000000',
            '+11111111111',
        ]
        msg = 'message in a bottle'
        sns.publish = Mock()
        sns.publish.return_value = {'MessageId': '0123'}
        SnsNotification(sns, phone_numbers).send(msg)

        sns.publish.assert_has_calls(
            calls=[
                call(PhoneNumber='+00000000000', Message=msg, MessageAttributes=self._MSG_ATTRIBUTES),
                call(PhoneNumber='+11111111111', Message=msg, MessageAttributes=self._MSG_ATTRIBUTES)
            ],
            any_order=True
        )

    def test_stdout_notification(self):
        StdoutNotification('ADDRESS').send('message')
