import pymysql
from scrapy import signals
import json
import time

from scrapy.exceptions import DropItem
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from sshtunnel import SSHTunnelForwarder

from AirbnbScrapySpider.config import Config  # 导入配置文件
from AirbnbScrapySpider.items import AirbnbRoomReviews
from AirbnbScrapySpider.pipelines import RoomsPipeline

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
            spider.browser.get(url=request.url)
            # 注入 cookie
            print("注入 cookie")
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
            # 如果是获取房屋详情界面，需要额外等待，确保评论加载完成
            WebDriverWait(spider.browser, 30, 1).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[4]/div/div/div/section/div[2]/div[5]"))
            )
            element = spider.browser.find_element_by_tag_name('body')
            element.send_keys(Keys.END)
            with SSHTunnelForwarder(
                    (config.server.ip, config.server.port),  # 指定ssh登录的跳转机的address，端口号
                    ssh_username=config.server.username,  # 跳转机的用户名
                    ssh_pkey=config.server.private_key_path,  # 私钥路径
                    ssh_private_key_password=config.server.private_key_password,  # 跳转机的用户密码
                    remote_bind_address=(config.mysql.host, config.mysql.port)) as server:  # mysql服务器的address，端口号
                # 建立数据库连接
                connection = pymysql.connect(host='127.0.0.1',  # 此处必须是是127.0.0.1
                                             port=server.local_bind_port,
                                             user=config.mysql.username,  # 数据库用户名
                                             passwd=config.mysql.password,  # 数据库密码
                                             db=config.mysql.database  # 数据库名称
                                             )
                # 创建操作游标
                cursor = connection.cursor()
                current_room_id = request.url.split("?")[0].split("/")[-1]
                ul = spider.browser.find_element(By.XPATH, "/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[4]/div/div/div/section/div[2]/div[6]/div/div[1]/div/div/div/nav/ul")
                lis = ul.find_elements_by_xpath('li')
                if len(lis) < 5:
                    page_num_total = len(lis) - 1
                else:
                    page_num_total = spider.browser.find_element(By.XPATH, "/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[4]/div/div/div/section/div[2]/div[6]/div/div[1]/div/div/div/nav/ul/li[4]/button/div").text
                    page_num_total = int(page_num_total)
                print("此房源有{}页评论".format(page_num_total))

                for page_num in range(page_num_total):
                    time.sleep(3)
                    reviews = None
                    # 直接在这里获取评论并保存
                    reviews = spider.browser.find_element(By.XPATH, "/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[4]/div/div/div/section/div[2]/div[5]").text.split("\n")
                    for i in range(int(len(reviews) / 3)):
                        review_content = reviews.pop()
                        review_time = reviews.pop()
                        review_user_name = reviews.pop()
                        review_type = 1 if "的回复" in review_user_name else 0
                        if review_type == 1:
                            temp = review_content
                            review_content = review_time
                            review_time = temp
                        review_room_id = current_room_id
                        try:
                            # 定义sql语句
                            sql = "INSERT INTO airbnb.reviews (review_content, review_room_id, review_time, review_user_name, review_type) VALUES ('{}', '{}','{}' ,'{}',{})".format(review_content, review_room_id, review_time, review_user_name, review_type)
                            print("=========================================")
                            print(sql)
                            print("=========================================")
                            # 执行sql语句
                            cursor.execute(sql)
                            # 保存修改
                            connection.commit()
                        except Exception:
                            connection.rollback()
                            print("changes have been rolled back")
                            break

                    if page_num < page_num_total - 1:  # page_num 从零开始
                        print("===============")
                        print("当前为{}页，一共有{}页".format(page_num, page_num_total))
                        print("===============")
                        if page_num == 0:
                            next_btn = spider.browser.find_element(By.XPATH, "/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[4]/div/div/div/section/div[2]/div[6]/div/div[1]/div/div/div/nav/ul/li[{}]/button".format(len(lis)))
                        else:
                            next_btn = spider.browser.find_element(By.XPATH, "/html/body/div[3]/div/main/div/div/div/div/div[2]/div/div[1]/div/div[4]/div/div/div/section/div[2]/div[6]/div/div[1]/div/div/div/nav/ul/li[{}]/button".format(len(lis) if len(lis) < 5 else 7))
                        spider.browser.execute_script("arguments[0].click();", next_btn)
            # 这里是 获取房源列表 和 获取房屋详情 的操作
            time.sleep(8)
            raw_html = spider.browser.page_source
            return HtmlResponse(url=spider.browser.current_url, body=raw_html, encoding="utf8", request=request)

    def process_response(self, request, response, spider):
        return HtmlResponse(url=spider.browser.current_url, body=response.body, encoding="utf8", request=request)

    def process_exception(self, request, exception, spider):
        return None

    def spider_opened(self, spider):
        pass
