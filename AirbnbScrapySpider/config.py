import yaml
from easydict import EasyDict
from selenium import webdriver


class Config:
    def __init__(self):
        with open('D:\\001-myCode\\PycharmProjects\\AirbnbScrapySpider\\config.yaml') as f:
            config = EasyDict(yaml.safe_load(f))
        self.airbnb = config.airbnb
        self.mysql = config.mysql
        super().__init__()

    def getDriver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument('--window-size=1900,1000')  # 设置窗口大小.
        options.add_argument('lang=zh_CN.UTF-8')
        driver = webdriver.Chrome(executable_path='AirbnbScrapySpider/spiders/chromedriver.exe', options=options)
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"}})
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        return driver
