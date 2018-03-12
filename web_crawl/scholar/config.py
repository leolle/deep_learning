import logging

# Define some constants

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
URL_SEARCH = "https://scholar.google.com/scholar?&q={query}&hl=zh-CN&as_sdt=0,5"
URL_NEXT = "https://scholar.google.com/scholar?start={start}&q={query}&hl=zh-CN&as_sdt=0,5"

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
LOGGER = logging.getLogger('scholar')
