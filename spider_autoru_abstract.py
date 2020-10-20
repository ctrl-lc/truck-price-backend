from spider_abstract import AbstractSpider

class AutoRuAbstractSpider(AbstractSpider):

    def is_captcha(self, response):
        return response.css("title::text").get() == "Ой!"

        
    def get_ads(self, response):
        return response.css(".ListingItem-module__container") or \
            response.css('.ListingCars-module__list .ListingItem-module__container')

    
    def get_next_page(self, response):
        return response.css('a.ListingPagination-module__next::attr(href)').get()


    def extract_common_data(self, ad):
        return {
            'price': ad.css('meta[itemprop="price"]::attr(content)').get(),
            'vat_included': ad.css('.ListingItem-module__withNds::text').get(),
            'year': ad.css('meta[itemprop="productionDate"]::attr(content)').get(),
            'mileage': ''.join(ad.css('div.ListingItem-module__kmAge::text').re('[0-9]+')),
            'location': ad.css('span.MetroListPlace_nbsp::text').get(),
            'url': ad.css('meta[itemprop="url"]::attr(content)').get(),
            'make': ad.css('meta[itemprop="brand"]::attr(content)').get(),
            'name': ad.css('meta[itemprop="name"]::attr(content)').get(),
            'supplier': ad.css('.ListingItem-module__salonName::text').get()
        }