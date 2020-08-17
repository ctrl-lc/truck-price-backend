import scrapy
import pathlib

class AutoRuAbstractSpider(scrapy.Spider):

    def parse(self, response):
        for ad in self.get_ads(response):
            yield self.parse_ad(ad)

        next_page = self.get_next_page(response)
        if next_page is not None:
            yield response.follow(next_page, self.parse)
        
    def get_ads(self, response):
        return response.css('.ListingCars-module__list .ListingItem-module__container')
    
    def parse_ad(self, ad):
        pass

    def get_next_page(self, response):
        return response.css('a.ListingPagination-module__next::attr(href)').get()

    def extract_common_data(self, ad):
        return {
            'price': ad.css('meta[itemprop="price"]::attr(content)').get(),
            'year': ad.css('meta[itemprop="productionDate"]::attr(content)').get(),
            'mileage': ''.join(ad.css('div.ListingItem-module__kmAge::text').re('[0-9]+')),
            'location': ad.css('span.MetroListPlace_nbsp::text').get(),
            'url': ad.css('meta[itemprop="url"]::attr(content)').get(),
            'make': ad.css('meta[itemprop="brand"]::attr(content)').get(),
            'name': ad.css('meta[itemprop="name"]::attr(content)').get(),
            'supplier': ad.css('.ListingItem-module__salonName::text').get()
        }
