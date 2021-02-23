import scrapy


class NatashaclubSpider(scrapy.Spider):
    name = 'natashaclub'
    allowed_domain = 'www.natashaclub.com'
    auth_id, auth_password = '', ''
    auth_token = ''

    ENTRIES_PER_PAGE = 100  # VALID RANGE: 20-100
    SHOW_NEW_ONLY = 0  # 0 = FALSE, 1 = TRUE

    NEXT_PAGE_LINK_SELECTOR = '#ContentDiv div.DataDiv td[colspan="3"] a:nth-last-child(2)'
    MESSAGE_HREF_SELECTOR = '#ContentDiv div.DataDiv form[name=msg_form] tr.table td:nth-child(5) a[href]'

    custom_settings = {
        'CONCURRENT_REQUESTS': 5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
        'CONCURRENT_REQUESTS_PER_IP': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': 0,
        'DOWNLOAD_DELAY': 0
    }

    START_URL = f'https://www.natashaclub.com/inbox.php?page=1&filterID=&filterStartDate=&filterEndDate=' \
                f'&filterNewOnly={SHOW_NEW_ONLY}&filterPPage={ENTRIES_PER_PAGE}'
    AUTH_URL = 'https://www.natashaclub.com/member.php'

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      'Chrome/45.0.2454.85 Safari/537.36',
        'Cookie': f'Language=English;testCookie=1;memberT={auth_token}'
    }

    @staticmethod
    def parse_cookies(response):
        return str(response.headers['Set-Cookie']).split(';')[0].split('=')[-1]

    def start_requests(self):
        self.logger.info("Authenticating the system")
        yield scrapy.FormRequest(url=self.AUTH_URL,
                                 formdata={'ID': self.auth_id, 'Password': self.auth_password},
                                 callback=self.authenticated)

    def authenticated(self, response):
        self.logger.info("Crawler authenticated successfully")
        self.auth_token = self.parse_cookies(response)

        self.logger.info(f"Using cookie token: {self.auth_token}")
        yield scrapy.Request(self.START_URL, callback=self.parse_table, headers=self.HEADERS)

    def parse_table(self, response):
        refs = [href.attrib['href'] for href in response.css(self.MESSAGE_HREF_SELECTOR)]

        for ref in refs:
            yield {
                'message': ref
            }

        next_page_link_element = response.css(self.NEXT_PAGE_LINK_SELECTOR)

        if next_page_link_element:
            yield scrapy.Request("https://" + self.allowed_domain + next_page_link_element.attrib['href'],
                                 callback=self.parse_table, headers=self.HEADERS)
