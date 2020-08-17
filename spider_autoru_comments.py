import scrapy
import pandas as pd
import pathlib

class CommentsSpider(scrapy.Spider):

    name = 'comments'
    
    start_urls = set(pd.read_csv('data/comment task - auto.ru.csv', delimiter=';')['link'])

    custom_settings = {
        'FEEDS': {
            pathlib.Path('data/comments - auto.ru - results.csv'): {
                'format': 'csv'
            }
        }
    }


    def parse(self, response):

        yield {
            'url': response.url,
            'comment': ' '.join(response.css('div.CardDescription__textInner span::text').getall())
        }
