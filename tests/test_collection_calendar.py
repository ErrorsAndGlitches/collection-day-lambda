from unittest import TestCase
import json
from httmock import HTTMock, urlmatch
from datetime import date

from cdl.collection_calendar import _FindAddressRequest, _FindAccountRequest, _TokenRequest, \
    _SolidWasteSummaryRequest, _SolidWasteCalendarRequest, _ServiceEndpoint, _ServiceCalendar, \
    CollectionCalendar


class TestFindAddress(TestCase):
    def test_find_address(self):
        with HTTMock(self._find_address_mock):
            self.assertEqual(
                _FindAddressRequest('STREET ADDRESS').response().prem_code(),
                'PREM_CODE'
            )

    @staticmethod
    @urlmatch(scheme='https', netloc='myutilities.seattle.gov', path='/rest/serviceorder/findaddress')
    def _find_address_mock(url, request):
        with open('tests/find-address-response.json') as file:
            return json.dumps(json.load(file))


class TestFindAccount(TestCase):
    def test_find_account(self):
        with HTTMock(self._find_account_mock):
            response = _FindAccountRequest('PREM_CODE').response()
            self.assertEqual(response.account_number(), 'ACCOUNT_NUMBER')
            self.assertEqual(response.company_cd(), 'SPU')

    @staticmethod
    @urlmatch(scheme='https', netloc='myutilities.seattle.gov', path='/rest/serviceorder/findAccount')
    def _find_account_mock(url, request):
        with open('tests/find-account-response.json') as file:
            return json.dumps(json.load(file))


class TestToken(TestCase):
    def test_token(self):
        with HTTMock(self._token_mock):
            response = _TokenRequest().response()
            self.assertEqual(response.authorization_header(), {
                'Authorization': 'bearer ACCESS_TOKEN'
            })

    @staticmethod
    @urlmatch(scheme='https', netloc='myutilities.seattle.gov', path='/rest/auth/guest')
    def _token_mock(url, request):
        with open('tests/token-response.json') as file:
            return json.dumps(json.load(file))


class TestSolidWasteSummary(TestCase):
    def test_summary(self):
        with HTTMock(self._summary_mock):
            response = _SolidWasteSummaryRequest({'Authorization': 'bearer ACCESS_TOKEN'}, 'ACCOUNT_NUMBER').response()
            self.assertEqual(response.person_id(), 'PERSON_ID')
            self.assertEqual(response.service_endpoints(), [
                _ServiceEndpoint('3bQKqgPmO00iNyQYQB1eSw==', 'Garbage'),
                _ServiceEndpoint('ItjML9wfL2Q1/T5pQ4Wr9w==', 'Recycle'),
                _ServiceEndpoint('8IyKDqqIxEczlp9ukS6lQg==', 'Food/Yard Waste'),
            ])

    @staticmethod
    @urlmatch(scheme='https', netloc='myutilities.seattle.gov', path='/rest/guest/swsummary')
    def _summary_mock(url, request):
        with open('tests/solid-waste-summary-response.json') as file:
            return json.dumps(json.load(file))


class TestSolidWasteCalendar(TestCase):
    def test_calendar(self):
        with HTTMock(self._calendar_mock):
            response = _SolidWasteCalendarRequest(
                {'Authorization': 'bearer ACCESS_TOKEN'}, 'ACCOUNT_NUMBER', 'PERSON_ID', 'COMPANY_CD',
                [
                    _ServiceEndpoint('3bQKqgPmO00iNyQYQB1eSw==', 'Garbage'),
                    _ServiceEndpoint('ItjML9wfL2Q1/T5pQ4Wr9w==', 'Recycle'),
                    _ServiceEndpoint('8IyKDqqIxEczlp9ukS6lQg==', 'Food/Yard Waste')
                ]
            ).response()
            self.assertEqual(response.service_calendars(), [
                _ServiceCalendar(
                    'Garbage',
                    [
                        date(year=2020, month=12, day=31),
                        date(year=2021, month=1, day=7),
                        date(year=2021, month=1, day=14),
                        date(year=2021, month=1, day=21),
                        date(year=2021, month=1, day=28)
                    ]
                ),
                _ServiceCalendar(
                    'Recycle',
                    [
                        date(year=2020, month=12, day=31),
                        date(year=2021, month=1, day=14),
                        date(year=2021, month=1, day=28)
                    ]
                ),
                _ServiceCalendar(
                    'Food/Yard Waste',
                    [
                        date(year=2020, month=12, day=31),
                        date(year=2021, month=1, day=7),
                        date(year=2021, month=1, day=14),
                        date(year=2021, month=1, day=21),
                        date(year=2021, month=1, day=28)
                    ]
                )
            ])

    @staticmethod
    @urlmatch(scheme='https', netloc='myutilities.seattle.gov', path='/rest/solidwastecalendar')
    def _calendar_mock(url, request):
        with open('tests/solid-waste-calendar-response.json') as file:
            return json.dumps(json.load(file))


class TestServiceCalendar(TestCase):
    def setUp(self):
        self._calendar = _ServiceCalendar(
            'Recycle',
            [
                date(year=2020, month=12, day=31),
                date(year=2021, month=1, day=14),
                date(year=2021, month=1, day=28)
            ]
        )

    def test_description(self):
        self.assertEqual(self._calendar.description, 'Recycle')

    def test_earliest_date(self):
        self.assertEqual(
            self._calendar.earliest_date(date(year=2021, month=1, day=7)),
            date(year=2021, month=1, day=14)
        )
        self.assertEqual(
            self._calendar.earliest_date(date(year=2021, month=1, day=13)),
            date(year=2021, month=1, day=14)
        )
        self.assertEqual(
            self._calendar.earliest_date(date(year=2021, month=1, day=14)),
            date(year=2021, month=1, day=14)
        )
        self.assertEqual(
            self._calendar.earliest_date(date(year=2021, month=1, day=15)),
            date(year=2021, month=1, day=28)
        )

    def test_earliest_date_missing(self):
        with self.assertRaises(Exception):
            self._calendar.earliest_date(date(year=2021, month=1, day=29)),

    def test_has_pickup(self):
        self.assertTrue(self._calendar.has_pickup(date(year=2021, month=1, day=14)))
        self.assertTrue(self._calendar.has_pickup(date(year=2021, month=1, day=28)))

    def test_does_not_have_pickup(self):
        self.assertFalse(self._calendar.has_pickup(date(year=2021, month=1, day=13)))
        self.assertFalse(self._calendar.has_pickup(date(year=2021, month=1, day=15)))
        self.assertFalse(self._calendar.has_pickup(date(year=2021, month=1, day=27)))
        self.assertFalse(self._calendar.has_pickup(date(year=2021, month=1, day=29)))


class TestCollectionCalendar(TestCase):
    _PATH_TO_FILE_MAP = {
        '/rest/serviceorder/findaddress': 'tests/find-address-response.json',
        '/rest/serviceorder/findAccount': 'tests/find-account-response.json',
        '/rest/auth/guest': 'tests/token-response.json',
        '/rest/guest/swsummary': 'tests/solid-waste-summary-response.json',
        '/rest/solidwastecalendar': 'tests/solid-waste-calendar-response.json'
    }

    def test_recycling(self):
        with HTTMock(self._calendar_mock):
            self.assertEqual(
                CollectionCalendar('STREET ADDRESS', date(year=2021, month=1, day=13)).next_collection_msg(),
                'Next pick up will be on Thu 14 Jan 2021 and will include [Garbage,Recycle,Food/Yard Waste]'
            )

    def test_no_recycling(self):
        with HTTMock(self._calendar_mock):
            self.assertEqual(
                CollectionCalendar('STREET ADDRESS', date(year=2021, month=1, day=15)).next_collection_msg(),
                'Next pick up will be on Thu 21 Jan 2021 and will include [Garbage,Food/Yard Waste]'
            )

    @staticmethod
    @urlmatch(scheme='https', netloc='myutilities.seattle.gov')
    def _calendar_mock(url, request):
        with open(TestCollectionCalendar._PATH_TO_FILE_MAP[url.path]) as file:
            return json.dumps(json.load(file))
