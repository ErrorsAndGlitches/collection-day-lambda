from unittest import TestCase
from unittest.mock import Mock, call

from cdl.notifications import SnsNotification, StdoutNotification


class TestCollectionInfo(TestCase):
    def test_sns_notification(self):
        sns = Mock()
        phone_numbers = [
            '+00000000000',
            '+11111111111',
        ]
        msg = 'message in a bottle'
        SnsNotification(sns, phone_numbers).send(msg)

        sns.publish.assert_has_calls(
            calls=[
                call(PhoneNumber='+00000000000', Message=msg),
                call(PhoneNumber='+11111111111', Message=msg)
            ],
            any_order=True
        )

    def test_stdout_notification(self):
        StdoutNotification('ADDRESS').send('message')
