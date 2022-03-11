import scrapy


class AirbnbRoomDetailItem(scrapy.Item):
    # 房源ID
    ID = scrapy.Field()
    # 房源名称
    name = scrapy.Field()
    # 房源图片列表
    img_list = scrapy.Field()
    # 房源价格
    price = scrapy.Field()
    # 房间数量
    count = scrapy.Field()
    # 类型
    shape = scrapy.Field()
    # 房源详情url
    url = scrapy.Field()
    # 房东姓名
    landlord_id = scrapy.Field()
    # 房东详情页面链接
    landlord_url = scrapy.Field()
    # 评论数量
    reviews_num = scrapy.Field()
    # 评论标签
    reviews_tag = scrapy.Field()
    # 房源位置信息
    room_position = scrapy.Field()
    # 房源介绍
    description = scrapy.Field()
    # 房源出行信息
    room_metro = scrapy.Field()
    # 房屋守则
    room_rule = scrapy.Field()


class AirbnbRoomItem(scrapy.Item):
    # 房源ID
    ID = scrapy.Field()
    # 房间数量
    count = scrapy.Field()
    # 类型
    shape = scrapy.Field()
    # 房源详情url
    url = scrapy.Field()


class AirbnbLandlordDetailItem(scrapy.Item):
    # 房东ID 30806636
    ID = scrapy.Field()
    # 房东姓名
    name = scrapy.Field()
    # 房东介绍
    description = scrapy.Field()
    # 国籍
    landlord_country = scrapy.Field()
    # 房东语言
    landlord_language = scrapy.Field()
    # 房东头像
    landlord_img = scrapy.Field()


