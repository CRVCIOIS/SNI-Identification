"""
items.py
---------

This module contains the definition of the items to be scraped by the NLPspider.

Classes:
--------
NLPspiderItem : This is the item class for the NLPspider. It defines the fields that will be scraped.

Modules:
--------
scrapy : This module provides all the core functionality of Scrapy, including items, spiders, and the core scraping functionality.

"""

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
