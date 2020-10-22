from scrapy import Spider, Request
from datetime import datetime
from enum import Enum

class RecordValidation(Enum):
    OK = 1
    SKIP = 0
    FATAL = -1


class AbstractSpider(Spider):

    def start_requests(self):
        for u in self.start_urls:
            yield Request(u, errback=self.errback)


    def parse(self, response):
        self.check_for_captcha(response)
            
        ads = self.get_ads(response)
        if not ads:
            self.save_page(response.selector.get())
            raise RuntimeError('No ads found')
        
        for ad in ads:
            record = self.parse_ad(ad)
            is_valid = self.validate(record)
            
            if is_valid == RecordValidation.OK:
                yield record
            
            elif is_valid == RecordValidation.SKIP:
                pass
            
            elif is_valid == RecordValidation.FATAL:
                self.save_page(ad.get())
                raise RuntimeError('Cannot parse a record')
                

        next_pages = self.get_next_page(response)
        if next_pages is not None:
            if isinstance(next_pages, str):
                next_pages = [next_pages]
            
            for page in next_pages:
                yield response.follow(page, self.parse)

        
    def check_for_captcha(self, response):
        if self.is_captcha(response):
            raise ValueError('Got a captcha')

    
    def errback(self, failure):
        # log all failures
        self.logger.error(repr(failure))


    def save_page(self, text):
        with open(self.get_save_filename(text), 'w', encoding = 'utf-8') as f:
            f.write(text)
            

    def get_save_filename(self, text):
        return f'temp/{self.name}-{datetime.now().strftime("%m%d-%H%M")}-{str(hash(text))[:6]}.html'
    
    
    def validate(self, record):
        return RecordValidation.OK