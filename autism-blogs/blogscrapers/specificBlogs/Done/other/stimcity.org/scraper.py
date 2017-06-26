import scrapy
from selenium import webdriver
import time
import os
from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.request import request_fingerprint

class CustomFilter(RFPDupeFilter):

  def request_seen(self, request):
        if self.file:
            self.file.write(fp + os.linesep)

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://stimcity.org/']
    custom_settings = {
        'RETRY_TIMES': 10,
        'DUPEFILTER_CLASS' : 'scraper.CustomFilter'
    }

    def parse (self, response):
      for href in response.xpath('//li[@id="archives-4"]/ul/li/a/@href'):
          if href.extract() != "":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      self.driver = webdriver.Firefox()
      self.driver.get(response.url)
      max_scroll = 20
      urls = []
      retry = []
      i = 0
      while i < max_scroll:
        current = self.driver.current_url
        if current not in urls:
          urls.append(current)
          #self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
          try:
            to_click =self.driver.find_element_by_xpath('//div[@id="infinite-handle"]/span/button')
            webdriver.common.action_chains.ActionChains(self.driver).move_to_element(to_click).click(to_click).perform()
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
          except:
            i = max_scroll
        elif current not in retry:
          retry.append(current)
          #self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
          #time.sleep(1)
          try:
            to_click =self.driver.find_element_by_xpath('//div[@id="infinite-handle"]/span/button')
            webdriver.common.action_chains.ActionChains(self.driver).move_to_element(to_click).click(to_click).perform()
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
          except:
            i = max_scroll
        else:
          i=max_scroll
      self.driver.quit()
      for url in urls:
        yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
      for href in response.xpath('//h2[@class="entry-title"]/a/@href'):
        full_url = (href.extract())
        yield scrapy.Request(full_url, callback=self.parse_post)


    def parse_post(self, response):
      try:
        stringdate = response.xpath('//div[@class="post-date"]/span/text()').extract()[0]
      except:
        stringdate = ""

      try:
        title = response.xpath('//h1[@class="entry-title"]/text()').extract()[0]
      except:
        title =""

      try:
        body = ""
        for content in response.xpath('//div[@class="entry"]//*[not(descendant::div[@class="wpcnt"]) and not(ancestor-or-self::div[@class="wpcnt"]) and not(descendant::div[@id="jp-post-flair"]) and not(ancestor-or-self::div[@id="jp-post-flair"])]/text()'):
          body = body + content.extract() + ' '
      except:
        body =""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="entry"]//*[not(descendant::div[@class="wpcnt"]) and not(ancestor-or-self::div[@class="wpcnt"]) and not(descendant::div[@id="jp-post-flair"]) and not(ancestor-or-self::div[@id="jp-post-flair"])]/@href'):
          extracted = href.extract()
          if '//stimcity.org/' not in extracted:
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