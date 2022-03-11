# AirbnbScrapySpider —- An Airbnb crawler based on scrapy and selenium

## Steps

Modify the content of the configuration file named `config_example.yaml` and rename it to `config.yaml`
Then run the login crawler first by running the following command in the project directory.

```shell
scrapy crawl loginSpider
```

The username and password you have written to the configuration file will be read to log in to Airbnb, then the spider will store the cookie information to `AirbnbScrapySpider/spiders/cookies.json`. The cookie is needed for subsequent crawls.