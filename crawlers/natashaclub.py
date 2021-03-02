import scrapy
import datetime

from dbcontext import Session
from services import DialogueService


class NatashaclubSpider(scrapy.Spider):
    name = 'natashaclub'
    allowed_domain = 'www.natashaclub.com'
    auth_id, auth_password, auth_token = '', '', ''

    ENTRIES_PER_PAGE = 100  # VALID RANGE: 20-100

    NEXT_PAGE_LINK_SELECTOR = '#ContentDiv div.DataDiv td[colspan="3"] a:nth-last-child(2)'
    MESSAGE_HREF_SELECTOR = '#ContentDiv div.DataDiv form[name=msg_form] tr.table td:nth-child(5) a[href]'
    MARKER_HREF_SELECTOR = '#ContentDiv div.DataDiv form[name=msg_form] tr.table td:nth-child(2) img'

    NEW_MARKER_LINK = '/templates/tmpl_nc/images_nc/new.gif'

    PROFILE_HREF_SELECTOR = 'tr.panel:nth-child(1) > td:nth-child(1) > a:nth-child(2)'
    PROFILE_NICKNAME_SELECTOR, PROFILE_MESSAGE_SELECTOR = 'li.profile_nickname::text', 'td.table::text'
    PROFILE_AGE_SELECTOR, PROFILE_LOCATION_SELECTOR = 'li.profile_age_sex::text', 'li.profile_location::text'
    PROFILE_TIMESTAMP_SELECTOR = 'tr.panel:nth-child(3) > td:nth-child(2)::text'

    AUTH_URL = 'https://www.natashaclub.com/member.php'

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      'Chrome/45.0.2454.85 Safari/537.36',
        'Cookie': f'Language=English;testCookie=1;memberT={auth_token}'
    }

    def __init__(self, **kwargs):
        """
        Initial parameters for web crawler
        """

        super().__init__(**kwargs)
        self.logger.info("Initiating crawler")

        self.auth_id = kwargs['auth_id']
        self.auth_password = kwargs['auth_password']
        self.show_new_only = 1 if kwargs['show_new_messages'] is True else 0
        self.store_db = kwargs['save_db']

        if self.store_db is True:
            self.logger.info("Creating DB engine session")
            self.session = Session()
            self.dialogue_service = DialogueService(self.session)

    def start_requests(self):
        """
        Crawler authentication phase
        """

        super().start_requests()
        self.logger.info("Authenticating the system")
        yield scrapy.FormRequest(url=self.AUTH_URL,
                                 formdata={'ID': self.auth_id, 'Password': self.auth_password},
                                 callback=self.authenticated)

    def authenticated(self, response):
        """
        Crawler first redirection, if authentication was successful
        """

        self.logger.info("Crawler authenticated successfully")
        self.auth_token = str(response.headers['Set-Cookie']).split(';')[0].split('=')[-1]

        self.logger.info(f"Using cookie token: {self.auth_token}")
        yield scrapy.Request(f'https://www.natashaclub.com/inbox.php?page=1&filterID=&filterStartDate=&filterEndDate='
                             f'&filterNewOnly={self.show_new_only}&filterPPage={self.ENTRIES_PER_PAGE}',
                             callback=self.parse_table, headers=self.HEADERS)

    def parse_table(self, response):
        """
        Crawler recursive messages table scrapping.
        Continues while 'Next' link is available on the page.
        """

        refs = [href.attrib['href'] for href in response.css(self.MESSAGE_HREF_SELECTOR)]
        markers = [marker.attrib['src'] for marker in response.css(self.MARKER_HREF_SELECTOR)]

        for ref, marker in zip(refs, markers):
            query = self.parse_query(ref)
            is_new = marker == self.NEW_MARKER_LINK

            yield scrapy.Request("https://" + self.allowed_domain + "/" + ref, callback=self.parse_message,
                                 headers=self.HEADERS, cb_kwargs=dict(query=query, is_new=is_new))

        next_page_link_element = response.css(self.NEXT_PAGE_LINK_SELECTOR)

        if next_page_link_element:
            yield scrapy.Request("https://" + self.allowed_domain + next_page_link_element.attrib['href'],
                                 callback=self.parse_table, headers=self.HEADERS)

    def parse_message(self, response, **kwargs):
        """
        Crawler message box data scrapping.
        """
        query, is_new = kwargs['query'], kwargs['is_new']
        profile_href = response.css(self.PROFILE_HREF_SELECTOR).attrib['href']
        profile_id = profile_href.split('=')[1]
        message_timestamp = response.css(self.PROFILE_TIMESTAMP_SELECTOR).getall()[1][1:-1]

        try:
            payload = {
                'account_id': self.auth_id,
                'sender_id': profile_id,
                'dialogue_id': query['message'],
                'send_time': datetime.datetime.strptime(message_timestamp, '%Y-%m-%d %H:%M:%S'),
                'viewed': is_new,
                'text': ''.join(response.css(self.PROFILE_MESSAGE_SELECTOR).getall())
            }

            if self.store_db is True:
                self.dialogue_service.record_dialogue(
                    dialogue_id=payload['dialogue_id'],
                    sender_id=payload['sender_id'],
                    send_time=payload['send_time'],
                    viewed=payload['viewed'],
                    sender_message=payload['text'],
                    receiver_id=payload['account_id'],
                )

            yield payload
        except Exception as ex:
            self.logger.error(ex)

    def close(self, reason):
        if self.store_db is True:
            self.logger.info("Closing DB engine session")
            self.session.close()

        super().close(self, reason)

    @staticmethod
    def parse_query(url: str) -> dict:
        query_string = url.split('?')[1]
        return {query_pair.split('=')[0]: query_pair.split('=')[1] for query_pair in query_string.split('&')}
