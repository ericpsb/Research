import scrapy
from selenium import webdriver
import time


class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://unstrangemind.com/']
    custom_settings = {
        'RETRY_TIMES': 100,
    }
    
    def __init__(self):
		self.driver = webdriver.Firefox()
    
    def parse(self, response):
		self.driver.get(response.url)
		for href in self.driver.find_elements_by_xpath('//span[@class="post-date"]/a'):
			yield scrapy.Request(href.get_attribute("href"), callback=self.parse_post)
		more = self.driver.find_elements_by_xpath('//a [@class = "post-nav-older"]')
		if more != []:
			yield scrapy.Request(more[0].get_attribute("href"), callback=self.parse)
		else:
			self.driver.quit()

    def parse_post(self, response):
      try:
        stringdate = response.xpath('//span [@class = "post-date"]/a/text()').extract()[0]
      except:
        stringdate = ""

      try:
        title = response.xpath('//h1[@class="post-title"]/a/text()').extract()[0]
      except:
        title =""

      try:
        body = ""
        for content in response.xpath('//div[@class="post-content"]/text()'):
        	body = body + content.extract() + ' '
        for content in response.xpath('//div[@class="post-content"]//*[not(descendant::div[@class="wpcnt"]) and not(ancestor-or-self::div[@class="wpcnt"]) and not(descendant::div[@id="jp-post-flair"]) and not(ancestor-or-self::div[@id="jp-post-flair"])]/text()'):
          body = body + content.extract() + ' '
      except:
        body =""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="entry"]//*[not(descendant::div[@class="wpcnt"]) and not(ancestor-or-self::div[@class="wpcnt"]) and not(descendant::div[@id="jp-post-flair"]) and not(ancestor-or-self::div[@id="jp-post-flair"])]/@href'):
          extracted = href.extract()
          if 'http://unstrangemind.com/' not in extracted:
            outgoing_links.append(extracted)
      except:
        outgoing_links = []
      


      yield {
          'date' : stringdate,
          'body' : body,
          'link': response.url,
          'title': title,
          'outgoing_links': outgoing_links
        }

