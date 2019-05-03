from unittest import TestCase
from unittest.mock import Mock

from cdl.cdl import collection_day_lambda_handler


class TestCdl(TestCase):
    def test_return_result(self):
        pass
        #result = collection_day_lambda_handler(Mock('event'), Mock('context'))
        #self.assertEqual(result['result'], 'success')
