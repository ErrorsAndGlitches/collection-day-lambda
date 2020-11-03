import requests
from sbp.sbp_response import SbpResponse

ENDPOINT = 'https://app.rockgympro.com/b/widget/?a=equery'
POST_DATA = {
    'fctrl_1': 'offering_guid',
    'offering_guid': 'bf2f93358e7b4cd1835284d0f368cd59',
    'fctrl_4': 'show_date',
    'show_date': '2020-11-04',  # to be replaced
}
SHOW_DATE_KEY = "show_date"


class SbpRequest(object):
    def __init__(self, date):
        self._date = date

    def response(self):
        post_data = POST_DATA.copy()
        post_data[SHOW_DATE_KEY] = self._date
        return SbpResponse(requests.post(ENDPOINT, data=post_data).text)
