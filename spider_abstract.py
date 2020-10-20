from scrapy import Spider, Request
from datetime import datetime


class AbstractSpider(Spider):

    def start_requests(self):
        for u in self.start_urls:
            yield Request(u, errback=self.errback)


    def parse(self, response):
        if self.is_captcha(response):
            raise ValueError('Got a captcha')
            
        ads = self.get_ads(response)
        if not ads:
            save_page(response.selector.get())
            raise RuntimeError('No ads found')
        
        for ad in ads:
            yield self.parse_ad(ad)

        next_page = self.get_next_page(response)
        if next_page is not None:
            yield response.follow(next_page, self.parse)

        
    def is_captcha(self, response):
        raise NotImplementedError
    
        
    def errback(self, failure):
        # log all failures
        self.logger.error(repr(failure))


    def get_ads(self, response):
        return NotImplementedError
    
    
    def parse_ad(self, ad):
        raise NotImplementedError


    def get_next_page(self, response):
        raise NotImplementedError


def save_page(text):
    with open(getfilename(text), 'w', encoding = 'utf-8') as f:
        f.write(text)
        

def getfilename(text):
    return f'{datetime.now().strftime("%m%d-%H%M")}-{str(hash(text))[:6]}.html'