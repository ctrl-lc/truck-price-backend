from pathlib import Path
from spider_abstract import RecordValidation
from urllib.parse import urljoin
from spider_drom_abstract import DromAbstractSpider


class DromSpider(DromAbstractSpider):

    name = 'drom_trucks'

    start_urls = [
        'https://spec.drom.ru/truck/truck-tractor/?goodPresentState%5B%5D=present&spectechDocuments%5B%5D=yes&spectechState%5B%5D=new&spectechState%5B%5D=used&year_max=2019'
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
                ad.css('div.bull-item__annotation-row').re_first(r'\s(\d+x\d+)'),
                
            'Supplier':
                ad.css('.ellipsis-text__left-side span::text').get()
        }
        
        return record
    
    
    def validate(self, record):
        required = {'URL', 'Name'}
        if required <= record.keys() and all(record[x] for x in required):
            return RecordValidation.OK

        if not record['Price']:
            return RecordValidation.SKIP
        
        return RecordValidation.FATAL