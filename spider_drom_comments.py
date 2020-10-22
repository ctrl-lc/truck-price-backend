import pathlib

import pandas as pd
from lxutils import config
from scraper_api import ScraperAPIClient
from scrapy.http.request import Request

from spider_drom_abstract import DromAbstractSpider


class CommentsSpider(DromAbstractSpider):

    name = 'drom - comments'
    
    start_urls = set(pd.read_csv('data/comment task - drom.csv', delimiter=';')['link'])

    custom_settings = {
        'FEEDS': {
            pathlib.Path('data/comment result - drom.csv'): {
                'format': 'csv'
            }
        },
        'LOG_FILE': 'scrapy.log',
        'LOG_LEVEL': 'INFO'
    }

    scraper_api_client = ScraperAPIClient(config['tokens']['scraper-api'])


    def start_requests(self):
        for url in self.start_urls:
            yield Request(self.scraper_api_client.scrapyGet(url))


    def parse(self, response):
        self.check_for_captcha(response)
        yield {
            'url': response.url,
            'comment': ' '.join(s.strip() for s in response.css("#bulletin .bulletinText p::text").getall())
        }
