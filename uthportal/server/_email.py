import imaplib

class ServerError(Exception):
    pass

class AuthenticationError(Exception):
    pass

IMAP_STD_PORT = 143
IMAP_SSL_PORT = 993

class EmailClient:
    def __init__(self, host, use_ssl=True):

        if use_ssl:
            port = IMAP_SSL_PORT
        else:
            port = IMAP_STD_PORT

        try:
            self.client = imaplib.IMAP4_SSL(host, port)
        except:
            raise ServerError

    def login(self, username, password):
        try:
            self.client.login(username, password)
        except:
            raise AuthenticationError

    def logout(self):
        self.client.logout()

    def get_new_ml(self, code, mark_seen=False):
        # Open the INBOX mailbox and search for emails that contains in the subject
        # the [code] string that means that an email comes from a mailing list
        self.client.select('INBOX', readonly=True)
        (response, message_ids) = self.client.search(None, '(UNSEEN SUBJECT "[%s]")' % code)

        # Empty string
        if not message_ids[0]:
            return list()

        mails = list()

        # Dictionary where we define what we need to fetch and the name of them
        # NOTE: BODY.PEEK does not mark as seen the mail while BODY does
        fetch_items = {'date':'(BODY.PEEK[HEADER.FIELDS (DATE)])',
                    'subject':'(BODY.PEEK[HEADER.FIELDS (SUBJECT)])',
                    'body':'(BODY.PEEK[TEXT])' }

        # If we want to mark the emails as seen we use BODY
        if mark_seen:
            for key in fetch_item:
                fetch_items[key].replace('BODY.PEEK', 'BODY')

        # For each message that we haven't seen we fetch the info we want
        ids_list = message_ids[0].split(' ')
        print ids_list
        for id in ids_list:
            mail = dict()
            for (item, criterion) in fetch_items.items():
                if item is 'body':
                    mail[item] = self.client.fetch(id,criterion)[1][0][1].strip()
                else:
                    print criterion
                    mail[item] = self._parse_header(self.client.fetch(id, criterion))

            # Add the new mail in the list
            mails.append( mail )

        # Close the mailbox!
        self.client.close()

        return mails

    def get_ml(self, code_list, mark_seen=False):
        return { code:self.get_new_ml(code,mark_seen) for code in code_list }

    def _parse_header(self, tuple):
        text = tuple[1][0][1]
        splitter = text.find(':')

        return text[splitter + 1:].strip()

if __name__ == '__main__':
    c = EmailClient('imap.gmail.com')
    c.login('uthportal.inf','VolosHack123456')
    ml = c.get_ml(['CE120','CE121'])
    c.logout()

    # Print the List
    for mails in ml.values():
        for mail in mails:
            for key in mail:
                print key + ':' +  mail[key]

