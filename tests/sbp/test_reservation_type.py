from unittest import TestCase
from sbp.reservation_type import reservation_type, _FITNESS


class TestReservationType(TestCase):
    def test_reservation_types(self):
        self.assertEqual(reservation_type('fitness'), _FITNESS)
