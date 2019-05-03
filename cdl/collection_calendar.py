from datetime import datetime, timedelta
from urllib.parse import quote

import pyjq
import requests


class CollectionCalendar(object):
    """
    The calendar is backed by the Seattle WARP system. Something that is strange is that in the request to the data
    endpoint, if the start date passes the middle of the month, then the endpoint will return the next month e.g. if the
    request starts on 15 May, then the month of May is returned (independent of the endpoint, I've tried setting it to
    zero). However, if the request starts on 16 May, then June is returned.
    """
    _BASE_URL = 'https://www.seattle.gov/UTIL/WARP/CollectionCalendar/GetCollectionDays' \
                '?pAddress={address}&pApp=CC&start={start_epoch_sec}&end={end_epoch_sec}'
    _DECEMBER = 12
    _JQ_TRANSFORM = '.[] | { "date": .start, "Garbage": .Garbage, "Recycling": .Recycling, ' \
                    '"FoodAndYardWaste": .FoodAndYardWaste }'

    def __init__(self, address, today):
        self._address = address
        self._today = today

    def next_collection(self):
        first_of_month = self._today.replace(day=1)
        collections = self._collections_after_today(first_of_month)
        if len(collections) != 0:
            return collections[0]

        collections = self._collections_after_today(self._next_month_date(first_of_month))
        return collections[0]

    def _collections_after_today(self, start_date):
        collection_data = self._one_month_collection_data(start_date)
        infos = [
            CollectionInfo.from_json(json_info)
            for json_info in pyjq.all(CollectionCalendar._JQ_TRANSFORM, collection_data)
        ]
        return [
            info
            for info in infos
            if self._today < info.pickup_date
        ]

    def _one_month_collection_data(self, start_date):
        end_date = start_date + timedelta(weeks=3)

        response = requests.get(CollectionCalendar._BASE_URL.format(
            address=quote(self._address.upper()),
            start_epoch_sec=start_date.strftime('%s'),
            end_epoch_sec=end_date.strftime('%s')
        ))
        self._check_response_success(response)

        return response.json()

    @staticmethod
    def _check_response_success(response):
        if response.status_code != 200:
            raise 'Failed to fetch calendar data: %s'.format(response.status_code)

    @staticmethod
    def _next_month_date(first_of_month):
        if first_of_month.month != CollectionCalendar._DECEMBER:
            return first_of_month.replace(month=first_of_month.month + 1)
        else:
            return first_of_month.replace(year=first_of_month.year + 1, month=1)


class CollectionInfo(object):
    @staticmethod
    def from_json(json_info):
        parsed_date = datetime.strptime(json_info['date'], '%a, %d %b %Y').date()
        return CollectionInfo(parsed_date, json_info['Garbage'], json_info['Recycling'], json_info['FoodAndYardWaste'])

    def __init__(self, pickup_date, garbage, recycling, food_and_yard_waste):
        self.pickup_date = pickup_date
        self.garbage = garbage
        self.recycling = recycling
        self.food_and_yard_waste = food_and_yard_waste

    def __str__(self):
        pickup_items = []
        if self.garbage:
            pickup_items.append("garbage")
        if self.recycling:
            pickup_items.append("recycling")
        if self.food_and_yard_waste:
            pickup_items.append("food and yard waste")
        return 'Next pick up will be on {} and will include [{}]'.format(
            self.pickup_date.strftime('%a, %d %b %Y'),
            ','.join(pickup_items)
        )
