# coding:utf-8
# author: 'lyb'
# Date:2018/8/23 9:41
import sys
from time import sleep
import re

from selenium.webdriver import DesiredCapabilities, Proxy
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery

from config import *
from db import UseMongo

cap = DesiredCapabilities.PHANTOMJS.copy()  # copy防止修改源码

# proxy = Proxy(
#     {
#         'proxyType': ProxyType.MANUAL,
#         'httpProxy': '115.196.48.131:9000'  # 代理ip和端口
#     }
# )

for key, value in HEADERS.items():
    cap['phantomjs.page.customHeaders.{}'.format(key)] = value

# proxy.add_to_capabilities(cap)


def main(num):
    """
        主程序
    :param num:  页数 
    :return: 
    """
    browser = webdriver.PhantomJS(service_args=SERVICE_ARGS,
                                  desired_capabilities=cap)  # 无界面浏览器，desired_capabilities，
    wait = WebDriverWait(browser, 10)
    browser.set_window_size(1400, 900)
    browser.get('https://www.qidian.com/rank/fin?dateType=3&page={}'.format(num))
    handle = browser.current_window_handle
    handles = browser.window_handles
    for newhandle in handles:
        if newhandle != handle:
            browser.switch_to.window(newhandle)
            browser.close()
            browser.switch_to.window(handle)
    # 打开窗口, 并关闭额外打开的data窗口
    for n in range(1, 21):
        if (num - 1) * 20 + n in existed_url_list:
            print(f'排行第{(num - 1) * 20 + n}已存在')
        else:
            items = open_info_of_novel(n, wait, browser)
            # print(browser.current_url)
            parse_content(n, num, browser, items)
            browser.close()
            browser.switch_to.window(handle)
            sleep(2)
    browser.quit()


def open_info_of_novel(n, wait, browser):
    """
        返回每个详情页的信息数据
    :param n:   对应的顺序
    :param wait:    
    :param browser: 
    :return: 
    """
    url_a = '#rank-view-list > div > ul > li:nth-child({}) > div.book-mid-info > h4 > a'.format(n)
    submit = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, url_a))
    )
    submit.click()
    handle = browser.current_window_handle
    handles = browser.window_handles
    # 对窗口进行遍历
    for newhandle in handles:
        # 筛选新打开的窗口B
        if newhandle != handle:
            # 切换到新打开的窗口B
            browser.switch_to.window(newhandle)
            sleep(5)
            html = browser.page_source
            doc = PyQuery(html)
            items = doc('.book-detail-wrap').items()
            return items


def parse_content(n, num, browser, items):
    """
        解析数据，并保存至MongoDB数据库
    :param n:   第n页
    :param num:     第num行
    :param browser:     browser 窗口
    :param items:   数据
    """
    for item in items:
        is_Complete = False
        while not is_Complete:
            try:
                chapter = re.search(r'.*?(\d+).*?', item.find('#J-catalogCount').text(), re.S).group(1)
                score_people = (re.search(r'.*?(\d+).*?', item.find('#j_userCount').html(), re.S)).group(1)
            except AttributeError:
                browser.refresh()
                sleep(5)
            else:
                is_Complete = True
        book = {
            'title': re.search(r"<em>(.*?)</em>", item.find('.book-info').html(), re.S).group(1),
            'author': item.find('.writer').text(),
            'intro': item.find('.book-intro').text(),
            'chapter': chapter,
            'score': item.find('#score1').text() + '.' + item.find('#score2').text(),
            'score_people': score_people,
            'tags': item.find('.tag').text().split('\n'),
            'number': (num - 1) * 20 + n,
            'url': browser.current_url
        }
        use_mongo.save_to_mongo(book)


def select_method():
    """
        根据设置，返回对应的已存在的去重列表
    :return: 
    """
    if CRAWL_OR_CHECK == 'crawl':
        print('开始爬取')
        existed_url_list = use_mongo.existed_url()
        return existed_url_list
    elif CRAWL_OR_CHECK == 'check':
        try:
            check_field_name = CHECK_FIELD_NAME
        except NameError:
            check_field_name = None
        if check_field_name:
            print('开始检测数据是否完整')
            existed_url_list = use_mongo.check_field(check_field_name)
            if existed_url_list == None:
                print('没有要爬取的任务,任务结束')
                sys.exit()
            else:
                return existed_url_list
        else:
            raise KeyError('请在config 配置 CHECK_FIELD_NAME')
    else:
        raise KeyError("你应该在config文件里设置正确的 CRAWL_OR_CHECK 值")


if __name__ == '__main__':
    use_mongo = UseMongo()       # 连接MongoDB
    existed_url_list = select_method()     # 获取已存在的数据，去重
    with ThreadPoolExecutor(MAX_THREAD) as executor:            # 开启多线程
        all_task = [executor.submit(main, i) for i in range(1, 26)]
        for future in as_completed(all_task):
            data = future.result()
    print('all task is done')




