# AirbnbScrapySpider —- An Airbnb crawler based on scrapy and selenium

## Steps

Edit the configuration file `config.yaml`.An example is as follows：

```yaml
airbnb:
  phone_number: YOUR_PHONE_NUMBER
  password: LOGIN_PASSWORD
```

Then run the login crawler first by running the following command in the project directory.

```shell
scrapy crawl loginSpider
```

The username and password you have written to the configuration file will be read to log in to Airbnb, then the spider will store the cookie information to `AirbnbScrapySpider/spiders/cookies.json`. b The cookie is needed for subsequent crawls.