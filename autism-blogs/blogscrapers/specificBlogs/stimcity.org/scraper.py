import scrapy
from selenium import webdriver
import time

class test_spider(scrapy.Spider):
	name = "scraper"
	start_urls = ['http://stimcity.org/']
	custom_settings = {
		'RETRY_TIMES': 100,
	}

	def __init__(self):
		self.driver = webdriver.Firefox()
		open("debug.txt", "w")
    
	def parse (self, response):
		self.driver.get(response.url)
		for month in self.driver.find_elements_by_xpath('//li[@id="archives-4"]/ul/li/a'):
			yield scrapy.Request(month.get_attribute("href"), callback=self.parse_month)
		self.driver.quit()
        	 
		  
	def parse_month(self, response):
		toclick = response.xpath('//div [@id = "infinite-handle"]')
		debug = open("debug.txt", "a")
		if toclick != []:
			debug.write(toclick[0])
		while toclick != []:
			for x in toclick:
				try: 
					x.click()
					time.sleep(1)
				except:
					time.sleep(.2)
			toclick = response.xpath('//div [@id = "infinite-handle"]')
		for href in response.xpath('//div[@class = "post-date"]/a/@href'):
			yield scrapy.Request(href.extract(), callback=self.parse_link)
	
	def parse_link(self, response):
		try:
			stringdate = response.xpath('//div[@class="post-date"]/span/text()').extract()[0]
		except:
			stringdate = ""
      
		try:
			title = response.xpath('//h1[@class="entry-title"]/text()').extract()[0]
		except:
			title = ""
      
		try:
			body = ""
			for content in response.xpath('//div[@class="entry"]//*[not(descendant::div[@class="wpcnt"]) and not (ancestor-or-self::div[@id="jp-post-flair"]) and not(ancestor-or-self::div[@class="wpcnt"]) and not(descendant::div[@id="jp-post-flair"]) and not(descendant::style) and not(ancestor-or-self::style)]/text()'):
				body = body + content.extract() + ' '
		except:
			body = ""
      
		try:
			outgoing_links = []
			for href in response.xpath('//div[@class="post-body entry-content"]/descendant-or-self::a/@href'):
				extracted = href.extract()
				if 'http://stimcity.org/' not in extracted:
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