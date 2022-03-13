from scrapy import signals
import json
import time
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from AirbnbScrapySpider.config import Config  # 导入配置文件

config = Config()
flags = {
    'login': 'login',
    'room_detail': 'room_detail',
    'homes_list': 'homes_list'
}


class AirbnbScrapySpiderDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # 如果是登录获取 cookie 的爬虫
        if request.meta.get('flag') == flags['login']:
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
            return HtmlResponse(url=spider.browser.current_url, request=request, body="登陆完成", encoding="utf-8")
        else:
            # 如果是获取房屋详细信息的爬虫，需要额外进行切换页面操作
            # if request.meta.get('flag') == 'room_detail':
            #     new_window = 'window.open("{}")'.format(request.url)
            #     spider.browser.execute_script(new_window)
            #     # 移动句柄，对新打开页面进行操作
            #     spider.browser.switch_to_window(spider.browser.window_handles[1])

            spider.browser.get(url=request.url)
            # 注入 cookie
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
            time.sleep(3)
            # 刷新界面
            spider.browser.get(url=request.url)
            # 更新 cookie
            dict_cookies = spider.browser.get_cookies()  # 获取list的cookies
            json_cookies = json.dumps(dict_cookies)  # 转换成字符串保存
            with open('AirbnbScrapySpider/spiders/cookies.json', 'w') as f:
                f.write(json_cookies)

        if request.meta.get('flag') == flags['room_detail']:
            # 如果是获取房屋详情界面，需要额外等待，确保评论加载完成，以及需要进行新标签页的关闭和切换
            WebDriverWait(spider.browser, 30, 1).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[4]/div/div/div/section"))
            )

        # 这里是 获取房源列表 和 获取房屋详情 的操作
        element = spider.browser.find_element_by_tag_name('body')
        element.send_keys(Keys.END)
        time.sleep(8)
        raw_html = spider.browser.page_source
        return HtmlResponse(url=spider.browser.current_url, body=raw_html, encoding="utf8", request=request)

    def process_response(self, request, response, spider):
        return HtmlResponse(url=spider.browser.current_url, body=response.body, encoding="utf8", request=request)

    def process_exception(self, request, exception, spider):
        return None

    def spider_opened(self, spider):
        pass
