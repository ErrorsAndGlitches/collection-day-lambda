from unittest import TestCase
from httmock import urlmatch, HTTMock
from datetime import date
from urllib import parse
import json

from cdl.collection_calendar import CollectionInfo, CollectionCalendar


class TestCollectionInfo(TestCase):
    def test_str(self):
        info = CollectionInfo(date(year=2019, month=5, day=2), garbage=True, recycling=False, food_and_yard_waste=True)
        self.assertEqual(
            str(info),
            'Next pick up will be on Thu, 02 May 2019 and will include [garbage,food and yard waste]'
        )

    def test_from_json(self):
        with open('tests/collection-info.json') as f:
            json_info = json.load(f)
        info = CollectionInfo.from_json(json_info)

        self.assertEqual(
            str(info),
            'Next pick up will be on Thu, 02 May 2019 and will include [garbage,food and yard waste]'
        )


class TestCollectionCalendar(TestCase):
    def test_next_collection_info_first_month(self):
        with HTTMock(self._collection_api_mock):
            today = date(year=2019, month=5, day=1)
            info = CollectionCalendar('Westminster, London SW1A 1AA, UK', today).next_collection()
            self.assertEqual(info.pickup_date, date(year=2019, month=5, day=2))

    def test_next_collection_info_before_end_of_month(self):
        with HTTMock(self._collection_api_mock):
            today = date(year=2019, month=5, day=29)
            info = CollectionCalendar('Westminster, London SW1A 1AA, UK', today).next_collection()
            self.assertEqual(info.pickup_date, date(year=2019, month=5, day=30))

    def test_next_collection_info_in_next_month(self):
        with HTTMock(self._collection_api_mock):
            today = date(year=2019, month=5, day=31)
            info = CollectionCalendar('Westminster, London SW1A 1AA, UK', today).next_collection()
            self.assertEqual(info.pickup_date, date(year=2019, month=6, day=6))

    @staticmethod
    @urlmatch(scheme='https', netloc=r'www.seattle.gov')
    def _collection_api_mock(url, request):
        start_time = int(parse.parse_qs(url.query)['start'][0])

        if start_time == int(date(year=2019, month=5, day=1).strftime('%s')):
            with open('tests/collection-api-may-2019.json', 'r') as f:
                return json.dumps(json.load(f))

        if start_time == int(date(year=2019, month=6, day=1).strftime('%s')):
            with open('tests/collection-api-jun-2019.json', 'r') as f:
                return json.dumps(json.load(f))

        raise 'Did not find any matching test data for {}'.format(start_time)
