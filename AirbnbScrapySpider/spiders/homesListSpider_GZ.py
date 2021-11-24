import scrapy
from selenium import webdriver

from AirbnbScrapySpider.config import Config  # 导入配置文件
from AirbnbScrapySpider.items import AirbnbHomeListItem

'''导入配置'''
config = Config()
'''配置 selenium'''
chrome_opt = webdriver.ChromeOptions()  # 创建参数设置对象.
# chrome_opt.add_argument('--headless')  # 无界面化.
# chrome_opt.add_argument('--disable-gpu')  # 配合上面的无界面化.
# chrome_opt.add_argument('--window-size=1900,1000')  # 设置窗口大小, 窗口大小会有影响.
# chrome_opt.add_argument('–disable-infobars')
# chrome_opt.add_argument('–incognito')
# chrome_opt.add_argument('lang=zh_CN.UTF-8')
chrome_opt.add_experimental_option('debuggerAddress', '127.0.0.1:9222')


class HomesListSpider(scrapy.Spider):
    name = 'homesListSpiderGZ'
    allowed_domains = ['airbnb.cn']
    start_urls = ['https://www.airbnb.cn/s/%E5%B9%BF%E5%B7%9E%E4%B8%9C%E7%AB%99/homes?refinement_paths%5B%5D=%2Fhomes&current_tab_id=home_tab&selected_tab_id=home_tab&pets=0&screen_size=large&hide_dates_and_guests_filters=false&place_id=ChIJpfPXL_D-AjQRuCzOwZURknI&map_toggle=false']

    def __init__(self, **kwargs):
        self.browser = webdriver.Chrome(executable_path='AirbnbScrapySpider/spiders/chromedriver.exe',
                                        options=chrome_opt)
        self.pageNum = 0
        super().__init__()

    def start_requests(self):
        response = scrapy.Request(self.start_urls[0], callback=self.custom_parse)
        yield response

    def custom_parse(self, response, **kwargs):
        for i in range(1, 21):
            try:
                item = AirbnbHomeListItem()
                item['name'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/div[2]/div/div/text()".format(i))[0].extract()
                img = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[1]/div[3]/div/div/div/a/div/img/@src".format(i)).extract_first()
                if not img:
                    img = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/a/div/img/@src".format(i)).extract_first()
                item['img'] = img
                item['price'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div/span/span/span/span/span[2]/text()".format(i))[0].extract()
                shape_and_count = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/div[1]/div/span/span/text()".format(i)).extract()
                item['shape'] = list(shape_and_count)[0]
                item['count'] = list(shape_and_count)[1]
                item['url'] = 'https://www.airbnb.cn' + response.xpath('/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/@href'.format(i)).extract_first()
                item['ID'] = response.xpath("/html/body/div[3]/div/main/div/div/div/div[3]/div/div/section/div/div/div/div/div/div[2]/div/div/div/div/div[{}]/div/div/div/div/div/div/div[2]/a/@href".format(i)).extract_first().split("?")[0].replace("/rooms/", "")
                # 获取更加详细的房屋信息，如评论等
                # yield scrapy.Request(url=item['url'], callback=self.parse_detail)
                yield item  # 将房屋列表存入数据库
            except:
                continue
        self.pageNum += 1
        # 每个地点只爬 50 页，共 1000 个数据
        if self.pageNum <= 50:
            next_url = self.start_urls[0] + "&items_offset=" + str(20 * self.pageNum)
            # print("======================================================next_url=======================================================================")
            # print(next_url)
            # print("======================================================================================================================================")
            # if next_url:
            response = scrapy.Request(next_url, callback=self.custom_parse, dont_filter=True)
            yield response

    # 对每一个房屋进行详细访问并解析
    def parse_detail(self, response):
        pass
        # yield scrapy.Request(url=landlord_detail_url, callback=self.parse_landlord_detail, meta={"item": item})  # 通过 参数meta 可以将item参数传递进 callback回调函数,再由 response.meta[...]取出来

    # 对每个房东的信息进行访问解析
    def parse_landlord_detail(self, response):
        pass
        # item = response.meta["item"]  # 获取从response回调函数由meta传过来的 item 值
        # yield item

    def close(self, response):
        self.browser.quit()
