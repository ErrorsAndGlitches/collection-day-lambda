class ReservationType(object):
    def __init__(self, name, guid, url):
        self._name = name
        self._guid = guid
        self._url = url

    @property
    def name(self):
        return self._name

    @property
    def guid(self):
        return self._guid

    @property
    def url(self):
        return self._url

    def __str__(self):
        return '[{}, {}, {}]'.format(self.name, self.guid, self.url)


_MAIN_FLOOR_CLIMBING = ReservationType(
    'main-floor-climbing',
    '09555ff2ddcf4de6bb7b1c888265e4fd',
    'https://seattleboulderingproject.com/reserve-main-floor-climbing'
)

_LOWER_FLOOR_CLIMBING = ReservationType(
    'lower-floor-climbing',
    '146adfaeb4664ed3ac49378f68ba8c9f',
    'https://seattleboulderingproject.com/reserve-lower-floor-climbing'
)

_CLIMBING = ReservationType(
    'climbing',
    'd1146438e0bd4197860d86ae34f5c3bd',
    'https://seattleboulderingproject.com/reserve-climbing'
)

_FITNESS = ReservationType(
    'fitness',
    'bf2f93358e7b4cd1835284d0f368cd59',
    'https://seattleboulderingproject.com/reserve-fitness'
)

_RESERVATION_TYPES = [
    sym_value
    for sym_name, sym_value in globals().items() if isinstance(sym_value, ReservationType)
]


def reservation_type(res_type_name):
    for res_type in _RESERVATION_TYPES:
        if res_type.name == res_type_name:
            return res_type

    raise Exception('Unable to find reservation type with name: "{}"'.format(res_type_name))
