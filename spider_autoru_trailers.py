import pathlib
from spider_autoru_abstract import AutoRuAbstractSpider

class TrailersSpider(AutoRuAbstractSpider):

    name = 'trailers'
    
    start_urls = [
        'https://auto.ru/rossiya/trailer/used/?output_type=list&sort=fresh_relevance_1-desc&trailer_type=ST_CURTAIN_ONBOARD&trailer_type=ST_ONBOARD&trailer_type=ST_REFRIGERATOR&trailer_type=ST_CURTAIN&year_from=2000'
    ]

    custom_settings = {
        'FEEDS': {
            pathlib.Path('data/autoru - trailers.csv'): {
                'format': 'csv'
            }
        },
        'LOG_FILE': 'scapy.log',
        'LOG_ENABLED': True,
        'LOG_LEVEL': 'INFO'
    }


    def parse_ad(self, ad):
        record = self.extract_common_data(ad)
        record.update({
            'VehicleType': ad.css('meta[itemprop="vehicleConfiguration"]::attr(content)').get(),
        })
        return record
