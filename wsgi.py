import os
import schedule
from crawlers import start_crawler
from main import app as application

if __name__ == "__main__":
    schedule.every().hour.do(start_crawler(auth_id=os.getenv('VAR_AUTH_ID'),
                                           auth_password=os.getenv('VAR_AUTH_PASSWORD'),
                                           show_new_messages=os.getenv('VAR_NEW_MESSAGES') == 'True',
                                           concurrent_requests=int(os.getenv('VAR_CONCURRENT_REQUESTS')),
                                           save_db=os.getenv('VAR_SAVE_DB') == 'True'))
    application.run(debug=True)
