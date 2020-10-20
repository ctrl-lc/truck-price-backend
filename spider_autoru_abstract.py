import scrapy

class AutoRuAbstractSpider(scrapy.Spider):

    def start_requests(self):
        for u in self.start_urls:
            yield scrapy.Request(u, errback=self.errback)


    def parse(self, response):
        self.check_for_captcha(response)
        for ad in self.get_ads(response):
            yield self.parse_ad(ad)

        next_page = self.get_next_page(response)
        if next_page is not None:
            yield response.follow(next_page, self.parse)

        
    def check_for_captcha(self, response):
        if response.css("title::text").get() == "Ой!":
            raise ValueError('Got a captcha')

        
    def errback(self, failure):
        # log all failures
        self.logger.error(repr(failure))


    def get_ads(self, response):
        ads = response.css(".ListingItem-module__container") or \
            response.css('.ListingCars-module__list .ListingItem-module__container')
        if ads:
            return ads
        else:
            save_page(response.selector.get())
            raise RuntimeError('No ads found')

    
    def parse_ad(self, ad):
        raise NotImplementedError


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


def save_page(text):
    with open(getfilename(text), 'w', encoding = 'utf-8') as f:
        f.write(text)
        

def getfilename(text):
    return f'{datetime.now().strftime("%m%d-%H%M")}-{str(hash(text))[:6]}.html'