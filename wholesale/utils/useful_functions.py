import time
import logging


def retry_request(request, retry_count=5, sleep_time=2):
    success = False
    last_request_time = 0
    response = None
    while not success:
        try:
            elapsed = time.time() - last_request_time
            if elapsed < sleep_time:
                time.sleep(sleep_time - elapsed)
            response = request()
            last_request_time = time.time()
            success = True
        except Exception as e:
            if retry_count > 1:
                logging.error("An exception ocured. Trying again.")
                logging.error(e)
                retry_count = retry_count - 1
                time.sleep(sleep_time)
            else:
                logging.critical("Maximum number of retries reached.")
                raise e
    return response
