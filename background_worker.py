from time import sleep


def worker_invites() -> None:
    """Send first messages in dialogue from 1:00 PM to 2:00 PM,
    works in background, time delta: 5 min"""
    # 5 min in seconds
    time_delta = 300

    while True:
        # code
        sleep(time_delta)


def worker_msg_sender() -> None:
    """Send messages with delay,
    works in background, time delta: 5 min"""
    time_delta = 300

    while True:
        # code
        sleep(time_delta)


def worker_inbox_updater() -> None:
    """Check inbox for all profiles with password
    and add new profiles which have written message,
    works in background, time delta: 5 min"""
    time_delta = 300

    while True:
        # code
        sleep(time_delta)
