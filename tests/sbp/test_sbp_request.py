import json
from unittest import TestCase
from datetime import datetime

from httmock import HTTMock, urlmatch

from sbp.sbp_request import SbpRequest
from sbp.sbp_response import TimeEntry
from sbp.reservation_type import _FITNESS, _CLIMBING


class TestSbpRequest(TestCase):
    def test_sbp_request_unknown_type(self):
        with self.assertRaises(Exception):
            self._run_request_test('sauna')

    def test_sbp_request_climbing_guid(self):
        self._run_request_test(_CLIMBING)

    def test_sbp_request(self):
        self._run_request_test(_FITNESS)

    def _run_request_test(self, reservation_type):
        with HTTMock(self._sbp_reservations_mock):
            # default value of strftime is 1900-01-01T00:00:00.000
            # https://docs.python.org/3/library/datetime.html#technical-detail
            self.assertEqual(
                SbpRequest('2020-11-03', reservation_type).response().time_entries(),
                [
                    TimeEntry(self._time(7), self._time(8), 0),
                    TimeEntry(self._time(7, 5), self._time(8, 30), 0),
                    TimeEntry(self._time(7, 30), self._time(9), 0),
                    TimeEntry(self._time(8), self._time(9, 30), 0),
                    TimeEntry(self._time(8, 30), self._time(10), 2),
                    TimeEntry(self._time(9), self._time(10, 30), 5),
                    TimeEntry(self._time(9, 30), self._time(11), 5),
                    TimeEntry(self._time(10), self._time(11, 30), 3),
                    TimeEntry(self._time(10, 30), self._time(12), 6),
                    TimeEntry(self._time(11), self._time(12, 30), 2),
                    TimeEntry(self._time(11, 30), self._time(13), 6),
                    TimeEntry(self._time(12), self._time(13, 30), 4),
                    TimeEntry(self._time(12, 30), self._time(14), 7),
                    TimeEntry(self._time(13), self._time(14, 30), 5),
                    TimeEntry(self._time(13, 30), self._time(15), 6),
                    TimeEntry(self._time(14), self._time(15, 30), 6),
                    TimeEntry(self._time(14, 30), self._time(16), 5),
                    TimeEntry(self._time(15), self._time(16, 30), 0),
                    TimeEntry(self._time(15, 30), self._time(17), 0),
                    TimeEntry(self._time(16), self._time(17, 30), 0),
                    TimeEntry(self._time(16, 30), self._time(18), 0),
                    TimeEntry(self._time(17), self._time(18, 30), 0),
                    TimeEntry(self._time(17, 30), self._time(19), 0),
                    TimeEntry(self._time(18), self._time(19, 30), 0),
                    TimeEntry(self._time(18, 30), self._time(20), 0),
                    TimeEntry(self._time(19), self._time(20, 30), 0),
                    TimeEntry(self._time(19, 30), self._time(21), 0),
                    TimeEntry(self._time(20), self._time(21, 30), 0),
                    TimeEntry(self._time(20, 30), self._time(22), 0),
                    TimeEntry(self._time(21), self._time(22), 0),
                ]
            )

    @staticmethod
    def _time(hour, minute=0):
        return datetime(1900, 1, 1, hour, minute)

    @staticmethod
    @urlmatch(scheme='https', netloc=r'app.rockgympro.com')
    def _sbp_reservations_mock(url, request):
        with open('tests/sbp/sbp-reservation-response.json') as f:
            return json.dumps(json.load(f))
