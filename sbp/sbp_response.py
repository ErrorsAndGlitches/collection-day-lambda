import re
from datetime import datetime
import json

from bs4 import BeautifulSoup

SPACES_REGEX = re.compile('(\d+)\s+space')


class OpeningsFilter(object):
    def __init__(self, response):
        self._response = response

    def time_entries(self):
        return [
            entry
            for entry in self._response.time_entries()
            if entry.has_openings()
        ]


class TimeFilter(object):
    def __init__(self, response, start_time, end_time):
        self._response = response
        self._start_time = start_time
        self._end_time = end_time

    def time_entries(self):
        return [
            entry
            for entry in self._response.time_entries()
            if entry.is_in_window(self._start_time, self._end_time)
        ]


class SbpResponse(object):
    def __init__(self, response):
        self._response = response

    def time_entries(self):
        response = json.loads(self._response)
        soup = BeautifulSoup(response['event_list_html'], 'html.parser')
        return [SbpResponse._time_entry(row) for row in soup.find_all('tr')]

    @staticmethod
    def _time_entry(row):
        time_range = [
            SbpResponse._parse_time(part.strip())
            for part in row.contents[1].text.strip().split(',')[2].strip().split('to')
        ]
        return TimeEntry(time_range[0], time_range[1], SbpResponse._num_slots(row.contents[3]))

    @staticmethod
    def _parse_time(time):
        try:
            return datetime.strptime(time, "%I:%M %p")
        except:
            return datetime.strptime(time, "%I %p")

    @staticmethod
    def _num_slots(availability):
        for strong in availability.select('strong'):
            strong.extract()
        text = availability.text.strip()

        if 'Full' in text:
            return 0
        if 'Available' in text:
            return 15  # it's about this number. It's not clear what the actual value is.

        return int(SPACES_REGEX.match(text).group(1))


class TimeEntry:
    def __init__(self, start_time, end_time, num_slots):
        self._start_time = start_time
        self._end_time = end_time
        self._num_slots = num_slots

    def is_in_window(self, start_time, end_time):
        return self._start_time >= start_time and self._end_time <= end_time

    def has_openings(self):
        return self._num_slots > 0

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "[{} - {}]: {}".format(
            self._start_time.strftime("%H:%M"),
            self._end_time.strftime("%H:%M"),
            self._num_slots
        )

    def __eq__(self, other):
        if not isinstance(other, TimeEntry):
            return False

        return self._start_time == other._start_time \
               and self._end_time == other._end_time \
               and self._num_slots == other._num_slots
