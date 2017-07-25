import scrapy
from selenium import webdriver
import time

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://bloom-parentingkidswithdisabilities.blogspot.com/']
    custom_settings = {
        'RETRY_TIMES': 100,
    }

    def __init__(self):
        self.driver = webdriver.Firefox()
    
    def parse (self, response):
        self.driver.get(response.url)
        topic1 = self.driver.find_elements_by_xpath('//div[@id="PageList2"]/div/ul/li/a')[1]
        yield scrapy.Request(topic1.get_attribute("href"), callback = self.parse_page)
        self.driver.quit()

    def parse_page (self, response):
        for href in response.xpath('//div[@class="readmore"]/a/@href'):
            yield scrapy.Request(href.extract(), callback=self.parse_link)
        if (response.xpath('//a [@class = "blog-pager-older-link"]/@href') != []):
            yield scrapy.Request(response.xpath('//a [@class = "blog-pager-older-link"]/@href')[0].extract(), self.parse_page)
    
    def parse_link(self, response):
        try:
            stringdate = response.xpath('//h2[@class="date-header"]/text()').extract()[0]
        except:
            stringdate = ""
      
        try:
            title = response.xpath('//h3[@class="post-title entry-title"]/a/text()').extract()[0]
        except:
            title = ""
      
        try:
            body = ""
            for content in response.xpath('//div[@class="post-body entry-content"]/* [not (descendant::div[@class="post-share-buttons"]) and not (ancestor-or-self::div[@class="post-share-buttons"])]/text()'):
                body = body + content.extract() + ' '
        except:
            body = ""
      
        try:
            outgoing_links = []
            for href in response.xpath('//div[@class="post-body entry-content"]/descendant-or-self::a/@href'):
                extracted = href.extract()
                if 'http://bloom-parentingkidswithdisabilities.blogspot.com/' not in extracted:
                    outgoing_links.append(extracted)
        except:
            outgoing_links=[]
      
        yield{
            'link': response.url,
            'date': stringdate,
            'body': body,
            'title': title,
            'outgoing_links': outgoing_links
        }