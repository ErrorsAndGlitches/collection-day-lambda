from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, MagicMock

from sbp.sbp_response import TimeFilter, TimeEntry, OpeningsFilter, SbpResponse


class TestFilters(TestCase):
    def test_time_filter(self):
        self.assertEqual(
            TimeFilter(self._mock_response(), self._time(7, 30), self._time(11)).time_entries(),
            [
                TimeEntry(self._time(7, 30), self._time(9), 0),
                TimeEntry(self._time(8), self._time(9, 30), 0),
                TimeEntry(self._time(8, 30), self._time(10), 2),
                TimeEntry(self._time(9), self._time(10, 30), 5),
                TimeEntry(self._time(9, 30), self._time(11), 5),
            ]
        )

    def test_openings_filter(self):
        self.assertEqual(
            OpeningsFilter(self._mock_response()).time_entries(),
            [
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
            ]
        )

    def test_sbp_response_available_type_opening(self):
        with open('tests/sbp/sbp-climbing-response-with-available-type.json') as f:
            self.assertEquals(
                SbpResponse(''.join(f.readlines())).time_entries(),
                [
                    TimeEntry(self._time(7), self._time(8), 0),
                    TimeEntry(self._time(7, 5), self._time(9), 0),
                    TimeEntry(self._time(7, 30), self._time(9, 30), 0),
                    TimeEntry(self._time(8), self._time(10), 0),
                    TimeEntry(self._time(8, 30), self._time(10, 30), 0),
                    TimeEntry(self._time(9), self._time(11), 7),
                    TimeEntry(self._time(9, 30), self._time(11, 30), 15),
                    TimeEntry(self._time(10), self._time(12), 14),
                    TimeEntry(self._time(10, 30), self._time(12, 30), 9),
                    TimeEntry(self._time(11), self._time(13), 10),
                    TimeEntry(self._time(11, 30), self._time(13, 30), 12),
                    TimeEntry(self._time(12), self._time(14), 12),
                    TimeEntry(self._time(12, 30), self._time(14, 30), 15),
                    TimeEntry(self._time(13), self._time(15), 5),
                    TimeEntry(self._time(13, 30), self._time(15, 30), 14),
                    TimeEntry(self._time(14), self._time(16), 1),
                    TimeEntry(self._time(14, 30), self._time(16, 30), 0),
                    TimeEntry(self._time(15), self._time(17), 0),
                    TimeEntry(self._time(15, 30), self._time(17, 30), 0),
                    TimeEntry(self._time(16), self._time(18), 0),
                    TimeEntry(self._time(16, 30), self._time(18, 30), 0),
                    TimeEntry(self._time(17), self._time(19), 0),
                    TimeEntry(self._time(17, 30), self._time(19, 30), 0),
                    TimeEntry(self._time(18), self._time(20), 0),
                    TimeEntry(self._time(18, 30), self._time(20, 30), 0),
                    TimeEntry(self._time(19), self._time(21), 0),
                    TimeEntry(self._time(19, 30), self._time(21, 30), 0),
                    TimeEntry(self._time(20), self._time(22), 0),
                    TimeEntry(self._time(20, 30), self._time(22), 0),
                    TimeEntry(self._time(21), self._time(22), 0),
                ]
            )

    def _mock_response(self):
        response = Mock()
        response.time_entries = MagicMock(return_value=[
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
        ])
        return response

    @staticmethod
    def _time(hour, minute=0):
        return datetime(1900, 1, 1, hour, minute)
