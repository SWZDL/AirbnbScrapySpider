import json
import random

import requests
import scrapy
from easydict import EasyDict
from selenium import webdriver

from AirbnbScrapySpider.config import Config  # 导入配置文件

'''导入配置'''
config = Config()
'''配置 selenium'''
chrome_opt = webdriver.ChromeOptions()  # 创建参数设置对象
# chrome_opt.add_argument('--headless')  # 无界面
# chrome_opt.add_argument('--disable-gpu')  # 禁用 GPU
chrome_opt.add_argument('--window-size=1900,1000')  # 设置窗口大小.
chrome_opt.add_experimental_option("excludeSwitches", ["enable-automation"])  # 去除正在受到自动测试软件的提示
chrome_opt.add_experimental_option('useAutomationExtension', False)  # 去除正在受到自动测试软件的提示
# chrome_opt.add_argument('-–incognito') # 隐私模式
chrome_opt.add_argument('lang=zh_CN.UTF-8')


class LoginSpider(scrapy.Spider):
    name = 'loginSpider'
    allowed_domains = ['airbnb.cn']
    start_urls = ['https://www.airbnb.cn/login/']

    def get_proxy(self):
        proxy = json.loads(requests.get("http://localhost:8899/api/v1/proxies?page=1").text)['proxies']
        proxy_list = list(proxy)
        # print(proxy_list)
        if len(proxy_list) > 0:
            random_ip_index = random.randint(1, len(proxy_list))
            ip = proxy_list[random_ip_index]['ip']
            port = proxy_list[random_ip_index]['port']
            return ip, port, True
        else:
            return 0, 0, False

    def __init__(self, **kwargs):
        ip, port, valid = self.get_proxy()
        if valid:
            chrome_opt.add_argument("--proxy-server=http://{}:{}".format(ip, port))
        self.browser = webdriver.Chrome(executable_path='AirbnbScrapySpider/spiders/chromedriver.exe', options=chrome_opt)
        super().__init__()

    def parse(self, response):
        pass

    def close(self, response):
        self.browser.quit()
