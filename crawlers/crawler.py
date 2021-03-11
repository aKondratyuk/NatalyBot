import asyncio
import datetime
import aiohttp

from db import DialogueService, Session
from lxml import html


class Crawler:
    ENTRIES_PER_PAGE = 100  # VALID RANGE: 20 - 100

    NEXT_PAGE_LINK_SELECTOR = '#ContentDiv div.DataDiv td[colspan="3"] a:nth-last-child(2)'
    MESSAGE_HREF_SELECTOR = '#ContentDiv div.DataDiv form[name=msg_form] tr.table td:nth-child(5) a[href]'
    MARKER_HREF_SELECTOR = '#ContentDiv div.DataDiv form[name=msg_form] tr.table td:nth-child(2) img'

    NEW_MARKER_LINK = '/templates/tmpl_nc/images_nc/new.gif'

    PROFILE_HREF_SELECTOR = 'tr.panel:nth-child(1) > td:nth-child(1) > a:nth-child(2)'
    PROFILE_NICKNAME_SELECTOR, PROFILE_MESSAGE_SELECTOR = 'li.profile_nickname', 'td.table'
    PROFILE_AGE_SELECTOR, PROFILE_LOCATION_SELECTOR = 'li.profile_age_sex', 'li.profile_location'
    PROFILE_TIMESTAMP_SELECTOR = 'tr.panel:nth-child(3) > td:nth-child(2)'

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

    async def parse_single_message(self, session, token, ref, query, is_new):
        async with session.get(ref, headers=self.form_headers(token)) as response:
            resp = await response.text()

            document = html.fromstring(resp)
            profile_hrefs = [refs.attrib['href'] for refs
                             in document.cssselect(self.PROFILE_HREF_SELECTOR)]

            message_timestamps = [stamp.text_content() for stamp
                                  in document.cssselect(self.PROFILE_TIMESTAMP_SELECTOR)]
            key_message_timestamp = message_timestamps[0].replace('\xa0Date:', '')[1:-1]

            if self.store_db is True:
                self.dialogue_service.record_dialogue(
                    dialogue_id=query['message'],
                    sender_id=profile_hrefs[0].split('=')[1],
                    send_time=datetime.datetime.strptime(key_message_timestamp, '%Y-%m-%d %H:%M:%S'),
                    viewed=is_new,
                    sender_message=''.join([chunk.text_content()
                                            for chunk in document.cssselect(self.PROFILE_MESSAGE_SELECTOR)]),
                    receiver_id=self.auth_id,
                )

    @staticmethod
    def form_headers(auth_token: str):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          'Chrome/45.0.2454.85 Safari/537.36',
            'Cookie': f'Language=English;testCookie=1;memberT={auth_token}'
        }

    @staticmethod
    def parse_url_query(url: str) -> dict:
        query_string = url.split('?')[1]
        return {query_pair.split('=')[0]: query_pair.split('=')[1] for query_pair in query_string.split('&')}

    async def index(self):
        form_data = {
            'ID': self.auth_id,
            'Password': self.auth_password
        }

        async with aiohttp.ClientSession() as session:
            response = await session.post(self.AUTH_URL, data=form_data)
            token = str(response.headers['Set-Cookie']).split(';')[0].split('=')[-1]

            print(f"Using authentication token: {token} for {self.auth_id}")
            await self.parse_tables(session, token)

    async def parse_tables(self, session, token):
        response = await session.get(f'https://www.natashaclub.com/inbox.php?page=1&filterID=&filterStartDate'
                                     f'=&filterEndDate=&'
                                     f'filterNewOnly={self.show_new_only}&filterPPage={self.ENTRIES_PER_PAGE}',
                                     headers=self.form_headers(token))

        document = html.fromstring(await response.text())
        next_page_link_element = document.cssselect(self.NEXT_PAGE_LINK_SELECTOR)

        while len(next_page_link_element) > 0:
            refs = [href.attrib['href'] for href in document.cssselect(self.MESSAGE_HREF_SELECTOR)]
            markers = [marker.attrib['src'] for marker in document.cssselect(self.MARKER_HREF_SELECTOR)]

            await asyncio.gather(*[self.parse_single_message(session,
                                                             token,
                                                             "https://www.natashaclub.com/" + ref,
                                                             self.parse_url_query(ref),
                                                             marker == self.NEW_MARKER_LINK)
                                   for ref, marker in
                                   zip(refs, markers)])

            next_page_link_element = []
