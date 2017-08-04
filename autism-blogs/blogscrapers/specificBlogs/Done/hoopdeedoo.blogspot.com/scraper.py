import scrapy
from selenium import webdriver
import time

class test_spider(scrapy.Spider):
	name = "scraper"
	start_urls = ['http://hoopdeedoo.blogspot.com/']
	custom_settings = {
		'RETRY_TIMES': 100,
	}

	def __init__(self):
		self.driver = webdriver.Firefox()
    
	def parse (self, response):
		self.driver.get(response.url)
		toclick = self.driver.find_elements_by_xpath('//span[@class="zippy"]')
		while toclick != []:
			for x in toclick:
				try: 
					x.click()
					time.sleep(1)
				except:
					time.sleep(.2)
			toclick = self.driver.find_elements_by_xpath('//span[@class="zippy"]')
		for month in self.driver.find_elements_by_xpath('//ul[@class = "hierarchy"]/li/ul/li/a'): 
			yield scrapy.Request(month.get_attribute("href"), callback=self.parse_month)
		self.driver.quit()
        	
		  
	def parse_month(self, response):
		for href in response.xpath('//a[@class = "timestamp-link"]/@href'):
			yield scrapy.Request(href.extract(), callback=self.parse_link)
	
	def parse_link(self, response):
		try:
			stringdate = response.xpath('//h2[@class="date-header"]/span/text()').extract()[0]
		except:
			stringdate = ""
      
		try:
			title = response.xpath('//h3[@class="post-title entry-title"]/text()').extract()[0]
		except:
			title = ""
      
		try:
			body = ""
			for content in response.xpath('//div[@class="post-body entry-content"]/descendant-or-self::node()/text()'):
				body = body + content.extract() + ' '
		except:
			body = ""
      
		try:
			outgoing_links = []
			for href in response.xpath('//div[@class="post-body entry-content"]/descendant-or-self::a/@href'):
				extracted = href.extract()
				if 'http://hoopdeedoo.blogspot.com/' not in extracted:
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