import scrapy
from db_models import Session


class NatashaclubSpider(scrapy.Spider):
    name = 'natashaclub'
    allowed_domain = 'www.natashaclub.com'
    auth_id, auth_password, auth_token = '', '', ''
    concurrent_requests = 5

    ENTRIES_PER_PAGE = 100  # VALID RANGE: 20-100

    NEXT_PAGE_LINK_SELECTOR = '#ContentDiv div.DataDiv td[colspan="3"] a:nth-last-child(2)'
    MESSAGE_HREF_SELECTOR = '#ContentDiv div.DataDiv form[name=msg_form] tr.table td:nth-child(5) a[href]'

    PROFILE_NICKNAME_SELECTOR, PROFILE_MESSAGE_SELECTOR = 'li.profile_nickname::text', 'td.table::text'
    PROFILE_AGE_SELECTOR, PROFILE_LOCATION_SELECTOR = 'li.profile_age_sex::text', 'li.profile_location::text'
    PROFILE_TIMESTAMP_SELECTOR = 'tr.panel:nth-child(3) > td:nth-child(2)::text'

    custom_settings = {
        'CONCURRENT_REQUESTS': concurrent_requests,
        'CONCURRENT_REQUESTS_PER_DOMAIN': concurrent_requests,
        'CONCURRENT_REQUESTS_PER_IP': concurrent_requests,
        'RANDOMIZE_DOWNLOAD_DELAY': 0,
        'DOWNLOAD_DELAY': 0
    }

    AUTH_URL = 'https://www.natashaclub.com/member.php'

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      'Chrome/45.0.2454.85 Safari/537.36',
        'Cookie': f'Language=English;testCookie=1;memberT={auth_token}'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger.info("Initiating crawler")

        self.auth_id = kwargs['auth_id']
        self.auth_password = kwargs['auth_password']
        self.concurrent_requests = kwargs['concurrent_requests']
        self.show_new_only = 1 if kwargs['show_new_messages'] is True else 0

    def start_requests(self):
        self.logger.info("Authenticating the system")
        yield scrapy.FormRequest(url=self.AUTH_URL,
                                 formdata={'ID': self.auth_id, 'Password': self.auth_password},
                                 callback=self.authenticated)

    def authenticated(self, response):
        self.logger.info("Crawler authenticated successfully")
        self.auth_token = str(response.headers['Set-Cookie']).split(';')[0].split('=')[-1]

        self.logger.info(f"Using cookie token: {self.auth_token}")
        yield scrapy.Request(f'https://www.natashaclub.com/inbox.php?page=1&filterID=&filterStartDate=&filterEndDate='
                             f'&filterNewOnly={self.show_new_only}&filterPPage={self.ENTRIES_PER_PAGE}',
                             callback=self.parse_table, headers=self.HEADERS)

    def parse_table(self, response):
        refs = [href.attrib['href'] for href in response.css(self.MESSAGE_HREF_SELECTOR)]

        for ref in refs:
            yield scrapy.Request("https://" + self.allowed_domain + "/" + ref, callback=self.parse_message,
                                 headers=self.HEADERS)

        next_page_link_element = response.css(self.NEXT_PAGE_LINK_SELECTOR)

        if next_page_link_element:
            yield scrapy.Request("https://" + self.allowed_domain + next_page_link_element.attrib['href'],
                                 callback=self.parse_table, headers=self.HEADERS)

    def parse_message(self, response):
        profile_age_sex = ''.join(response.css(self.PROFILE_AGE_SELECTOR).getall())

        try:
            payload = {
                'profile_nickname': ''.join(response.css(self.PROFILE_NICKNAME_SELECTOR).getall()),
                'profile_age': int(profile_age_sex.split()[0]),
                'profile_sex': str(profile_age_sex.split()[2]),
                'profile_location': ''.join(response.css(self.PROFILE_LOCATION_SELECTOR).getall()),
                'profile_message': ''.join(response.css(self.PROFILE_MESSAGE_SELECTOR).getall()),
                'profile_timestamp': response.css(self.PROFILE_TIMESTAMP_SELECTOR).getall()[1][1:-1]
            }

            yield payload
        except Exception as ex:
            self.logger.error(ex)
