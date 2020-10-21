import pandas as pd
import pathlib

from spider_drom_abstract import DromAbstractSpider

class CommentsSpider(DromAbstractSpider):

    name = 'drom - comments'
    
    start_urls = set(pd.read_csv('data/comments task - drom.csv', delimiter=';')['link'])

    custom_settings = {
        'FEEDS': {
            pathlib.Path('data/comments - drom - results.csv'): {
                'format': 'csv'
            }
        },
        'LOG_FILE': 'scrapy.log',
        'LOG_LEVEL': 'INFO'
    }


    def parse(self, response):
        self.check_for_captcha(response)
        yield {
            'url': response.url,
            'comment': ' '.join(response.css("#bulletin .bulletinText").get_all())
        }
