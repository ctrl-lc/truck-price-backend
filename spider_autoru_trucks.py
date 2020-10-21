import pathlib
from spider_abstract import RecordValidation
from spider_autoru_abstract import AutoRuAbstractSpider

class TrucksSpider(AutoRuAbstractSpider):
    
    name = 'autoru - trucks'
    
    start_urls = [
        'https://auto.ru/rossiya/artic/all/?output_type=list&sort=fresh_relevance_1-desc&year_from=2000&year_to=2004',
        'https://auto.ru/rossiya/artic/all/?output_type=list&sort=fresh_relevance_1-desc&year_from=2005&year_to=2009',
        'https://auto.ru/rossiya/artic/all/?output_type=list&sort=fresh_relevance_1-desc&year_from=2009&year_to=2014',
        'https://auto.ru/rossiya/artic/all/?output_type=list&sort=fresh_relevance_1-desc&year_from=2015&year_to=2019'
    ]

    custom_settings = {
        'FEEDS': {
            pathlib.Path('data/autoru - trucks.csv'): {
                'format': 'csv'
            }
        },
        'LOG_FILE': 'scrapy.log',
        'LOG_LEVEL': 'INFO'
    }


    def parse_ad(self, ad):
        record = self.extract_common_data(ad)
        record.update({
            'gear': ad.css('meta[itemprop="vehicleTransmission"]::attr(content)').get(),
            'hp': ad.css('meta[itemprop="enginePower"]::attr(content)').re(r'\d+')[0]
        })
            
        try:
            record.update({
                'formula': ad.css('.ListingItemTechSummaryDesktop__column')[1]
                        .css('.ListingItemTechSummaryDesktop__cell')[0]
                        .css('::text').get()
            })
        except IndexError:
            pass

        try:
            record.update({
                'cab': ad.css('.ListingItemTechSummaryDesktop__column')[0]
                        .css('.ListingItemTechSummaryDesktop__cell')[1]
                        .css('::text').get()
            })
        except IndexError:
            pass

        return record
    
    
    def validate(self, record):
        return RecordValidation.OK if (
            super().validate(record) == RecordValidation.OK and 
            {'hp', 'gear'} <= record.keys()
        ) else RecordValidation.FATAL