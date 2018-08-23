# coding:utf-8
__author__ = 'lyb'
# Date:2018/8/23 9:42

DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
  'Accept-Language': 'en',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6716.400 QQBrowser/1',
  'Host': 'www.qidian.com',
  'Connection': 'keep-alive',
  'Accept-Encoding': 'gzip, deflate, br',
}

SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']

HEADERS = {'User-Agent': DEFAULT_REQUEST_HEADERS}

MAX_THREAD = 5

MONGO_URI = 'your'
MONGO_DB = 'your'
MONGO_TABLE = 'your'

# crawl or check
CRAWL_OR_CHECK = 'crawl'

# if CRAWL_OR_CHECK is check, set this value
# CHECK_FIELD_NAME = 'url'
