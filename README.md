# AirbnbScrapySpider —- An Airbnb crawler based on scrapy and selenium

## Steps

Edit the configuration file `config.yaml`.An example is as follows：

```yaml
airbnb:
  phone_number: YOUR_PHONE_NUMBER
  password: LOGIN_PASSWORD
mysql:
  username:
  password:
  database:
chrome_options:
  arguments: [ '--headless', '--disable-gpu','--window-size=1900,1000','–disable-infobars','–incognito','lang=zh_CN.UTF-8' ]
```

Then run the login crawler first by running the following command in the project directory.

```shell
scrapy crawl loginSpider
```

The username and password you have written to the configuration file will be read to log in to Airbnb, then the spider will store the cookie information to `AirbnbScrapySpider/spiders/cookies.json`. The cookie is needed for subsequent crawls.