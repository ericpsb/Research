import scrapy
from selenium import webdriver
import time

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://www.lovethatmax.com/']
    custom_settings = {
        'RETRY_TIMES': 10,
    }

    def __init__(self):
        self.driver = webdriver.Firefox()
    
    def parse (self, response):
      self.driver.get(response.url)
      toclick = self.driver.find_elements_by_xpath('//span[@class="zippy"]')
      for x in toclick:
        webdriver.common.action_chains.ActionChains(self.driver).move_to_element(x).click(x).perform()
        time.sleep(1)
      for href in self.driver.find_elements_by_xpath('//ul[@class="posts"]/li/a'):
            full_url = response.urljoin(href.get_attribute("href"))
            yield scrapy.Request(full_url, callback=self.parse_link)
      self.driver.close()
    
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
        for content in response.xpath('//div[@class="post-body entry-content"]/text() | //div[@class="post-body entry-content"]//*[not(descendant::div[@class="linkwithin_outer"]) and not(ancestor-or-self::div[@class="linkwithin_outer"])]/text()'):
          body = body + content.extract() + ' '
      except:
        body = ""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="post-body entry-content"]/a/@href | //div[@class="post-body entry-content"]//*[not(descendant::div[@class="linkwithin_outer"]) and not(ancestor-or-self::div[@class="linkwithin_outer"])]/a/@href'):
          extracted = href.extract()
          if 'http://www.lovethatmax.com' not in extracted:
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