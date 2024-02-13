# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy



class NLPspiderItem(scrapy.Item):
    """
    NLPspiderItem is a class that defines the fields for the items to be scraped by the NLPspider.

    Attributes:
    -----------
    url : scrapy.Field
        The URL of the page to be scraped.
    raw_html : scrapy.Field
        The raw HTML content of the page to be scraped.
    domain : scrapy.Field
        The domain name of the page to be scraped.
    """
    # define the fields for your item here like:
    domain = scrapy.Field()
    url = scrapy.Field()
    raw_html = scrapy.Field()
    pass
