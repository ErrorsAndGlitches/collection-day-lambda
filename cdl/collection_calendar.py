import pyjq
import requests
from datetime import datetime

_HTTP_OKAY = 200


def _check_status_code(response, obj):
    if response.status_code != _HTTP_OKAY:
        raise Exception('Bad response for request {}. Value: {}'.format(type(obj), response.status_code))


class CollectionCalendar(object):
    def __init__(self, address, today_date):
        """
        :param str address: address to look up collections for
        :param date today_date: date from which to look forward for the next pick up
        """
        self._address = address
        self._today_date = today_date

    def next_collection_msg(self):
        address_response = _FindAddressRequest(self._address).response()
        account_response = _FindAccountRequest(address_response.prem_code()).response()
        token_response = _TokenRequest().response()
        sw_summary_response = _SolidWasteSummaryRequest(
            token_response.authorization_header(), account_response.account_number()
        ).response()
        sw_calendar_response = _SolidWasteCalendarRequest(
            token_response.authorization_header(), account_response.account_number(), sw_summary_response.person_id(),
            account_response.company_cd(), sw_summary_response.service_endpoints()
        ).response()

        calendars = sw_calendar_response.service_calendars()
        earliest_date = sorted([
            calendar.earliest_date(self._today_date)
            for calendar in calendars
        ])[0]

        pickup_items = []
        for calendar in calendars:
            if calendar.has_pickup(earliest_date):
                pickup_items.append(calendar.description)

        return 'Next pick up will be on {} and will include [{}]'.format(
            datetime.strftime(earliest_date, '%a %d %b %Y'),
            ','.join(pickup_items)
        )


class _FindAddressRequest(object):
    _END_POINT = 'https://myutilities.seattle.gov/rest/serviceorder/findaddress'

    def __init__(self, address):
        self._address = address

    def response(self):
        resp = requests.post(
            self._END_POINT,
            json={
                'address': {
                    'addressLine1': self._address,
                    'city': '',
                    'zip': ''
                }
            },
            headers={'Content-Type': 'application/json'}
        )
        _check_status_code(resp, self)
        return _FindAddressResponse(resp.json())


class _FindAddressResponse(object):
    _PREM_CODE_JQ = '.address[0].premCode'

    def __init__(self, json_response):
        self._json_response = json_response

    def prem_code(self):
        return pyjq.one(self._PREM_CODE_JQ, self._json_response)


class _FindAccountRequest(object):
    _END_POINT = 'https://myutilities.seattle.gov/rest/serviceorder/findAccount'

    def __init__(self, prem_code):
        self._prem_code = prem_code

    def response(self):
        resp = requests.post(
            self._END_POINT,
            json={
                'address': {
                    'premCode': self._prem_code
                }
            },
            headers={'Content-Type': 'application/json'}
        )
        _check_status_code(resp, self)
        return _FindAccountResponse(resp.json())


class _FindAccountResponse(object):
    _ACCOUNT_NUMBER_JQ = '.account.accountNumber'
    _COMPANY_CD_JQ = '.account.companyCd'

    def __init__(self, json_response):
        self._json_response = json_response

    def account_number(self):
        return pyjq.one(self._ACCOUNT_NUMBER_JQ, self._json_response)

    def company_cd(self):
        return pyjq.one(self._COMPANY_CD_JQ, self._json_response)


class _TokenRequest(object):
    _END_POINT = 'https://myutilities.seattle.gov/rest/oauth/token'

    def response(self):
        resp = requests.post(
            self._END_POINT,
            data='grant_type=password&username=guest&password=guest',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic d2ViQ2xpZW50SWRQYXNzd29yZDpzZWNyZXQ='
            }
        )
        _check_status_code(resp, self)
        return _TokenResponse(resp.json())


class _TokenResponse(object):
    _TOKEN_TYPE_JQ = '.token_type'
    _ACCESS_TOKEN_JQ = '.access_token'

    def __init__(self, json_response):
        self._json_response = json_response

    def authorization_header(self):
        return {
            'Authorization': '{} {}'.format(self._token_type(), self._access_token())
        }

    def _token_type(self):
        return pyjq.one(self._TOKEN_TYPE_JQ, self._json_response)

    def _access_token(self):
        return pyjq.one(self._ACCESS_TOKEN_JQ, self._json_response)


class _SolidWasteSummaryRequest(object):
    _END_POINT = 'https://myutilities.seattle.gov/rest/account/swsummary'

    def __init__(self, authorization_header, account_number):
        self._authorization_header = authorization_header
        self._account_number = account_number

    def response(self):
        resp = requests.post(
            self._END_POINT,
            json={
                'customerId': 'guest',
                'accountContext': {
                    'accountNumber': self._account_number,
                    'personId': None,
                    'companyCd': None,
                    'serviceAddress': None
                }
            },
            headers={
                **{'Content-Type': 'application/json'},
                **self._authorization_header
            }
        )
        _check_status_code(resp, self)
        return _SolidWasteSummaryResponse(resp.json())


class _SolidWasteSummaryResponse(object):
    """
    The summary response information is not accurate and thus we need to query the calendar API.
    """

    def __init__(self, json_response):
        self._json_response = json_response

    def person_id(self):
        return pyjq.one('.accountSummaryType.personId', self._json_response)

    def service_endpoints(self):
        return [
            _ServiceEndpoint(service['servicePointId'], service['description'])
            for service in pyjq.all(
                '.accountSummaryType.swServices[0].services[] | { servicePointId: .servicePointId, description: .description }',
                self._json_response
            )
        ]


class _ServiceEndpoint(object):
    def __init__(self, endpoint_id, description):
        self.id = endpoint_id
        self.description = description

    def __eq__(self, other):
        return isinstance(other, _ServiceEndpoint) and self.id == other.id and self.description == other.description


class _SolidWasteCalendarRequest(object):
    _END_POINT = 'https://myutilities.seattle.gov/rest/solidwastecalendar'

    def __init__(self, authorization_header, account_number, person_id, company_cd, service_endpoints):
        self._authorization_header = authorization_header
        self._account_number = account_number
        self._person_id = person_id
        self._company_cd = company_cd
        self._service_endpoints = service_endpoints

    def response(self):
        resp = requests.post(
            self._END_POINT,
            json={
                'customerId': 'guest',
                'accountContext': {
                    'accountNumber': self._account_number,
                    'personId': self._person_id,
                    'companyCd': self._company_cd
                },
                'servicePoints': [endpoint.id for endpoint in self._service_endpoints]
            },
            headers={
                **self._authorization_header,
                **{'Content-Type': 'application/json'}
            }
        )
        _check_status_code(resp, self)
        return _SolidWasteCalendarResponse(resp.json(), self._service_endpoints)


class _SolidWasteCalendarResponse(object):
    _DATE_FORMAT = '%m/%d/%Y'

    def __init__(self, response, service_endpoints):
        self._response = response
        self._service_endpoints = service_endpoints

    def service_calendars(self):
        return [
            _ServiceCalendar(
                endpoint.description,
                [
                    datetime.strptime(date, self._DATE_FORMAT).date()
                    for date in pyjq.one('.calendar."{}"'.format(endpoint.id), self._response)
                ]
            )
            for endpoint in self._service_endpoints
        ]


class _ServiceCalendar(object):
    def __init__(self, description, pickup_dates):
        self._description = description
        self._pickup_dates = pickup_dates

    def earliest_date(self, current_date):
        for pickup_date in self._pickup_dates:
            if pickup_date >= current_date:
                return pickup_date
        raise Exception('Could not find pick up date after {}'.format(current_date))

    def has_pickup(self, date):
        return date in self._pickup_dates

    @property
    def description(self):
        return self._description

    def __eq__(self, other):
        return isinstance(other, _ServiceCalendar) and self._description == other._description \
               and self._pickup_dates == other._pickup_dates
