import requests
from sbp.sbp_response import SbpResponse

_ENDPOINT = 'https://app.rockgympro.com/b/widget/?a=equery'
_POST_DATA = {
    'fctrl_1': 'offering_guid',
    'offering_guid': '',  # to be replaced
    'fctrl_4': 'show_date',
    'show_date': '2020-11-04',  # to be replaced
}
_SHOW_DATE_KEY = "show_date"
_OFFERING_GUID_KEY = "offering_guid"
_FITNESS_OFFERING_GUID = 'bf2f93358e7b4cd1835284d0f368cd59'
_CLIMBING_OFFERING_GUID = 'd1146438e0bd4197860d86ae34f5c3bd'


class SbpRequest(object):
    def __init__(self, date, reservation_type):
        self._date = date
        self._reservation_type = reservation_type

    def response(self):
        post_data = _POST_DATA.copy()
        post_data[_SHOW_DATE_KEY] = self._date
        post_data[_OFFERING_GUID_KEY] = self._offering_guid()
        return SbpResponse(requests.post(_ENDPOINT, data=post_data).text)

    def _offering_guid(self):
        if self._reservation_type == 'climbing':
            return _CLIMBING_OFFERING_GUID
        elif self._reservation_type == 'fitness':
            return _FITNESS_OFFERING_GUID
        else:
            raise 'Unknown reservation type: "{}"'.format(self._reservation_type)
