class SbpEmail(object):
    def __init__(self, entries, from_email, to_email, reservation_type, ses):
        self._entries = entries
        self._from_email = from_email
        self._to_email = to_email
        self._reservation_type = reservation_type
        self._ses = ses

    def send(self):
        self._ses.send_email(
            Source=self._from_email,
            Destination={
                'ToAddresses': [self._to_email],
                'CcAddresses': [],
                'BccAddresses': []
            },
            Message={
                'Subject': {
                    'Data': 'Opening SBP fitness slots exist!'
                },
                'Body': {
                    'Html': {
                        'Data': self._body()
                    }
                }
            },
        )

    def _body(self):
        entries_body = ["<li>{}</li>".format(entry) for entry in self._entries]

        html = [
            "<a href=\"{}\">reservation page for {}</a>".format(self._reservation_type.url, self._reservation_type.name),
            "<br/>",
            "<br/>",
            "<ol>",
        ]
        html.extend(entries_body)
        html.append("</ol>")

        return "".join(html)
