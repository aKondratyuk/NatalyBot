import aiohttp
from db import DialogueService, Session


class Crawler:
    ENTRIES_PER_PAGE = 100  # VALID RANGE: 20 - 100

    NEXT_PAGE_LINK_SELECTOR = '#ContentDiv div.DataDiv td[colspan="3"] a:nth-last-child(2)'
    MESSAGE_HREF_SELECTOR = '#ContentDiv div.DataDiv form[name=msg_form] tr.table td:nth-child(5) a[href]'
    MARKER_HREF_SELECTOR = '#ContentDiv div.DataDiv form[name=msg_form] tr.table td:nth-child(2) img'

    NEW_MARKER_LINK = '/templates/tmpl_nc/images_nc/new.gif'

    PROFILE_HREF_SELECTOR = 'tr.panel:nth-child(1) > td:nth-child(1) > a:nth-child(2)'
    PROFILE_NICKNAME_SELECTOR, PROFILE_MESSAGE_SELECTOR = 'li.profile_nickname::text', 'td.table::text'
    PROFILE_AGE_SELECTOR, PROFILE_LOCATION_SELECTOR = 'li.profile_age_sex::text', 'li.profile_location::text'
    PROFILE_TIMESTAMP_SELECTOR = 'tr.panel:nth-child(3) > td:nth-child(2)::text'

    AUTH_URL = 'https://www.natashaclub.com/member.php'

    def __init__(self, **kwargs):
        """
        Initial parameters for web crawler
        """
        print("Initiating crawler")

        self.auth_id = kwargs['auth_id']
        self.auth_password = kwargs['auth_password']
        self.show_new_only = 1 if kwargs['show_new_messages'] is True else 0
        self.store_db = kwargs['save_db']

        if self.store_db is True:
            print("Creating DB engine session")

            self.session = Session()
            self.dialogue_service = DialogueService(self.session)

    @staticmethod
    def form_headers(auth_token: str):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          'Chrome/45.0.2454.85 Safari/537.36',
            'Cookie': f'Language=English;testCookie=1;memberT={auth_token}'
        }

    async def index(self):
        form_data = {
            'ID': self.auth_id,
            'Password': self.auth_password
        }

        async with aiohttp.ClientSession() as session:
            response = await session.post(self.AUTH_URL, data=form_data)
            token = str(response.headers['Set-Cookie']).split(';')[0].split('=')[-1]

        return token
