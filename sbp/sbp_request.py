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


class SbpRequest(object):
    def __init__(self, date, reservation_type):
        self._date = date
        self._reservation_type = reservation_type

    def response(self):
        post_data = _POST_DATA.copy()
        post_data[_SHOW_DATE_KEY] = self._date
        post_data[_OFFERING_GUID_KEY] = self._reservation_type.guid
        return SbpResponse(requests.post(_ENDPOINT, data=post_data).text)
