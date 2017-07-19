import scrapy
from selenium import webdriver
import time

# Subclass of scrapy.Spider
class test_spider(scrapy.Spider):
	# unique name
    name = "scraper"
    # place where the spider starts
    start_urls = ['http://autismsucksrocks.blogspot.com/']
    # extra random settings
    custom_settings = {
    	# presumably the number of times a spider will try to fulfill a request
        'RETRY_TIMES': 100,
    }

    def __init__(self):
        self.driver = webdriver.Firefox()
    
    # tells the spider how to deal with the response
    def parse (self, response):
      self.driver.get(response.url)
      # find any span elements wil the class name "zippy" (sidebar arrows) and click on them to see more links
      toclick = self.driver.find_elements_by_xpath('//span[@class="zippy"]')
      while toclick != []:
        for x in toclick:
          try: 
            x.click()
            time.sleep(1)
          except:
            time.sleep(.2)
        toclick = self.driver.find_elements_by_xpath('//span[@class="zippy"]')
      
      # Getting links from posts and requesting that they be followed and analyzed
      for href in self.driver.find_elements_by_xpath('//ul[@class="posts"]/li/a'):
            full_url = response.urljoin(href.get_attribute("href"))
            yield scrapy.Request(full_url, callback=self.parse_link)
      self.driver.quit()
    
    
    def parse_link(self, response):
    # using xpath to get the date
      try:
        stringdate = response.xpath('//h2[@class="date-header"]/span/text()').extract()[0]
      except:
        stringdate = ""
    # using xpath to get the title  
      try:
        title = response.xpath('//h3[@class="post-title entry-title"]/text()').extract()[0]
      except:
        title = ""
      
      # getting the body via xpath
      try:
        body = ""
        for content in response.xpath('//div[@class="post-body entry-content"]/descendant-or-self::node()/text()'):
          body = body + content.extract() + ' '
      except:
        body = ""
      # not sure if these are relevant... don't think they are
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="post-body entry-content"]/descendant-or-self::a/@href'):
          extracted = href.extract()
          if 'http://autismsucksrocks.blogspot.com/' not in extracted:
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