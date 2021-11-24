import yaml
from easydict import EasyDict


class Config:
    def __init__(self):
        with open('D:\\001-myCode\\PycharmProjects\\AirbnbScrapySpider\\config.yaml') as f:
            config = EasyDict(yaml.safe_load(f))
        self.airbnb = config.airbnb
        self.mysql = config.mysql
        self.chrome_options = config.chrome_options
        super().__init__()
