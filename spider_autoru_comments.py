import pandas as pd
import pathlib

from spider_autoru_abstract import AutoRuAbstractSpider

class CommentsSpider(AutoRuAbstractSpider):

    name = 'autoru - comments'
    
    start_urls = set(pd.read_csv('data/comment task - auto.ru.csv', delimiter=';')['link'])

    custom_settings = {
        'FEEDS': {
            pathlib.Path('data/comments - auto.ru - results.csv'): {
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
            'comment': ' '.join(response.css('div.CardDescription__textInner span::text').getall())
        }
