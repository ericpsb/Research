import scrapy
from selenium import webdriver
import time

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://www.stimeyland.com/']
    custom_settings = {
        'RETRY_TIMES': 100,
    }

    def __init__(self):
        self.driver = webdriver.Firefox()
    
	def parse (self, response):
		self.driver.get(response.url)
		toclick = self.driver.find_elements_by_xpath('//span[@class="sym"]')
		while toclick != []:
			for x in toclick:
				try: 
					x.click()
					time.sleep(1)
				except:
					time.sleep(.2)
			toclick = self.driver.find_elements_by_xpath('//span[@class="sym"]')
		for href in self.driver.find_elements_by_xpath('//li[@class="collapsing archives item"]/a'):
			full_url = response.urljoin(href.get_attribute("href"))
			yield scrapy.Request(full_url, callback=self.parse_link)
		self.driver.close()
    
    def parse_link(self, response):
      try:
        stringdate = response.xpath('//time[@class="entry-date"]/text()').extract()[0]
      except:
        stringdate = ""
      
      try:
        title = response.xpath('//h1[@class="entry-title"]/text()').extract()[0]
      except:
        title = ""
      
      try:
        body = ""
        for content in response.xpath('//div[@class="entry-content"]/text() | //div[@class="entry-content"]//*[not(descendant::div[@class="sharedaddy sd-sharing-enabled"]) and not(ancestor-or-self::div[@class="sharedaddy sd-sharing-enabled"])]/text()'):
          body = body + content.extract() + ' '
      except:
        body = ""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="entry-content"]/a/@href | //div[@class="entry-content"]//*[not(descendant::div[@class="sharedaddy sd-sharing-enabled"]) and not(ancestor-or-self::div[@class="sharedaddy sd-sharing-enabled"])]/a/@href'):
          extracted = href.extract()
          if 'http://www.stimeyland.com' not in extracted:
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