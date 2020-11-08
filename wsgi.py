from threading import Thread

from background_worker import worker_profile_and_msg_updater
from main import app as application

if __name__ == "__main__":
    t1 = Thread(target=worker_profile_and_msg_updater)
    t1.start()
    application.run(debug=True)
