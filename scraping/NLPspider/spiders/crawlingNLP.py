"""
This module contains the CrawlingnlpSpider class, which is a Scrapy spider for crawling and scraping websites for the NLP project.
"""
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse
from NLPspider.items import NLPspiderItem
import tldextract


class CrawlingnlpSpider(CrawlSpider):
    """
    Spider for crawling and scraping websites for the NLP project.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the CrawlingnlpSpider.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
                start_urls (str): Comma-separated list of URLs to start crawling from.
        """
        super(CrawlingnlpSpider, self).__init__(*args, **kwargs)

        self.start_urls = kwargs.get("start_urls").split(
            ",")  # Get the start_urls from the kwargs
        allowed = set()  # `set()` to keep every domain only once

        allowed_TLDS = ["se", "com", "org", "net", "nu"]
        for link in self.start_urls:
            """
            Loop through the start_urls and extract the domain name from
            each URL.

            Adds se, com, org, net, nu TLD to allowed domains.
            """
            
            url = tldextract.extract(link) 
            allowed.add(f"{url.domain}.{url.suffix}")
            for TLD in allowed_TLDS:
                domain = f"{url.domain}.{TLD}"
                allowed.add(domain)

        self.allowed_domains = list(allowed)
        self.logger.debug(f"Start URLs: {self.start_urls}")
        self.logger.debug(f"Allowed domains: {self.allowed_domains}")
        self.rules = (
            Rule(LinkExtractor(allow_domains=self.allowed_domains),
                 callback="parse_item", follow=True),
        )
        # This is needed to compile the rules after we have changed them
        super(CrawlingnlpSpider, self)._compile_rules()

    name = "crawlingNLP"

    def parse_item(self, response):
        """
        Parse the scraped item from the response.

        Args:
            response (scrapy.http.Response): The response object.

        Yields:
            dict: The scraped item.
        """
        item = NLPspiderItem()
        item['domain'] = f'{tldextract.extract(response.url).domain}.{tldextract.extract(response.url).suffix}'
        item["url"] = response.url
        item["raw_html"] = response.text

        yield item
