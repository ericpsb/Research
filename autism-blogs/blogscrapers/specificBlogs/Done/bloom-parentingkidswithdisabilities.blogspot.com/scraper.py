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
      archive_click = self.driver.find_element_by_xpath('/html/body/div/div/div/div[7]/div[5]/div[4]/div/ul/li[3]/a')
      webdriver.common.action_chains.ActionChains(self.driver).move_to_element(archive_click).click(archive_click).perform()
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
        stringdate = response.xpath('//h2[@class="date-header"]/text()').extract()[0]
        i = stringdate.find(',') + 1
        if i != 0:
          stringdate = stringdate[i:]
      except:
        stringdate = ""
      
      try:
        title = response.xpath('//h3[@class="post-title entry-title"]/a/text()').extract()[0]
      except:
        title = ""
      
      try:
        body = ""
        for content in response.xpath('//div[@class="post-body entry-content"]/text() | //div[@class="post-body entry-content"]//*[not(descendant::div[@class="post-share-buttons"]) and not(ancestor-or-self::div[@class="post-share-buttons"])]/text()'):
          body = body + content.extract() + ' '
      except:
        body = ""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="post-body entry-content"]/a/@href | //[@class="post-body entry-content"]//*[not(descendant::div[@class="post-share-buttons"]) and not(ancestor-or-self::div[@class="post-share-buttons"])]/a/@href'):
          extracted = href.extract()
          if 'http://bloom-parentingkidswithdisabilities.blogspot.com' not in extracted and extracted !='':
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
      