from spider_abstract import AbstractSpider


class DromAbstractSpider(AbstractSpider):

    def is_captcha(self, response):
        return response.selector.re('Мы зарегистрировали подозрительный траффик')


    def get_ads(self, response):
        return response.css('.bull-item')
    
    
    def get_next_page(self, response):
        return response.css('.pagebar a::attr(href)').getall()