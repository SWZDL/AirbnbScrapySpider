import json
import time

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from AirbnbScrapySpider.config import Config  # 导入配置文件

'''导入配置'''
config = Config()


class AirbnbscrapyspiderDownloaderMiddleware:

    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        """
        三个参数:
        # request: 响应对象所对应的请求对象
        # response: 拦截到的响应对象
        # spider: 爬虫文件中对应的爬虫类 homesListSpider_GZ.py 的实例对象, 可以通过这个参数拿到 homes_list 中的一些属性或方法
        """
        #  对页面响应体数据的篡改, 如果是每个模块的 url 请求, 则处理完数据并进行封装

        # 如果是登录获取 cookie 的爬虫
        if spider.name == "loginSpider":
            spider.browser.get(request.url)
            WebDriverWait(spider.browser, 300, 1).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/main/div/div[2]/div/div/div[2]/div[2]/label/div/div/div/div"))
            )

            spider.browser.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div/div[2]/div[2]/label/div/div/div/div").click()
            spider.browser.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div/div[1]/div[2]/div/div/div[2]/div/span[1]/button/div/div[2]/div").click()
            spider.browser.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div/div[1]/div/form/div/div[2]/div[1]/div/div/div/div/div/input").send_keys(
                config.airbnb.phone_number)
            spider.browser.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div/div[1]/div/form/div/div[2]/div[2]/div/div/div/div[2]/input").send_keys(
                config.airbnb.password)

            spider.browser.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div/div[1]/div/form/div/div[5]/div/div/div[3]/div/button").click()
            # 保存登陆完成的 cookies
            WebDriverWait(spider.browser, 300, 1).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div[1]/div/header/div/div/div[3]/div/div/nav/ul/li[10]/div/div/div/button/div"))
            )
            dict_cookies = spider.browser.get_cookies()  # 获取list的cookies
            json_cookies = json.dumps(dict_cookies)  # 转换成字符串保存
            with open('AirbnbScrapySpider/spiders/cookies.json', 'w') as f:
                f.write(json_cookies)

        # 如果是获取房源的爬虫
        elif spider.name == "homesListSpider":
            spider.browser.get(url=request.url)
            # 写入 cookie
            with open('AirbnbScrapySpider/spiders/cookies.json', 'r', encoding='utf8') as f:
                cookies_list = json.loads(f.read())
            for cookie in cookies_list:
                cookie_dict = {
                    'domain': cookie.get('domain'),
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    'path': cookie.get('path'),
                    'httpOnly': cookie.get('httpOnly'),
                    'secure': cookie.get('secure')
                }
                spider.browser.add_cookie(cookie_dict)
            # 刷新界面
            spider.browser.get(url=request.url)
            time.sleep(3)
            element = spider.browser.find_element_by_tag_name('body')
            element.send_keys(Keys.END)
            time.sleep(10)
            row_response = spider.browser.page_source
            return HtmlResponse(url=spider.browser.current_url, body=row_response, encoding="utf8", request=request)

        elif spider.name == "roomDetailSpider":
            # 或许房屋详情的爬虫
            spider.browser.get(request.url)
            time.sleep(3)
            element = spider.browser.find_element_by_tag_name('body')
            element.send_keys(Keys.END)
            row_response = spider.browser.page_source
            return HtmlResponse(url=spider.browser.current_url, body=row_response, encoding="utf8", request=request)

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        # spider.browser.quit()
        return None


    def spider_opened(self, spider):
        # print('Spider opened: %s' % spider.name)
        pass
