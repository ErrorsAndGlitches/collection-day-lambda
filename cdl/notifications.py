from termcolor import colored


class StdoutNotification(object):
    def __init__(self, address):
        self._address = address

    def send(self, msg):
        print(colored('Pick up status for "{}":'.format(self._address), 'green'))
        print(msg)


class SnsNotification(object):
    def __init__(self, sns, phone_numbers):
        self._sns = sns
        self._phone_numbers = phone_numbers

    def send(self, msg):
        for phone_number in self._phone_numbers:
            self._sns.publish(
                PhoneNumber=phone_number,
                Message=msg
            )
