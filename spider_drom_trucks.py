from pathlib import Path
from urllib.parse import urljoin
from spider_abstract import AbstractSpider, save_page


class DromSpider(AbstractSpider):

    name = 'drom_trucks'

    start_urls = [
        'https://spec.drom.ru/truck/truck-tractor/'
    ]

    custom_settings = {
        'FEEDS': {
            Path('data/drom - trucks.csv'): {
                'format': 'csv'
            }
        },
        'LOG_FILE': 'scrapy.log',
        'LOG_LEVEL': 'INFO'
    }


    def is_captcha(self, response):
        return False


    def get_ads(self, response):
        return response.css('.bull-item')
    
    
    def parse_ad(self, ad):
        record = {
            'URL': 
                urljoin('https://spec.drom.ru/',
                    ad.css('div.bull-item-content__description a::attr("href")').get() or
                    ad.css('div.title a::attr("href")').get()
                ),
                
            'Name': 
                ad.css('div.bull-item-content__description a::text').get() or
                ad.css('div.title a::text').get(),
                
            'Price': 
                ad.css('span.price-block__price::text').get(),
            
            'Location': 
                ad.css('span.bull-delivery__city::text').get() or
                ad.css('div.ellipsis-text__left-side span::text').get(),
            
            'Formula': 
                ad.css('div.bull-item__annotation-row').re_first(r'\s(\d?x\d?)')
        }
        
        if not all(record[key] for key in ['URL', 'Name']):
            save_page(ad.get())
            raise RuntimeError('Some compulsory data missing')

        if not record['Price']:
            return
        
        return record


    def get_next_page(self, response):
        return response.css('.pagebar a::attr(href)').getall()