"""Change start_urls to desired blogspot blog
Also change condition for outgoing links """

import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://autismsedges.blogspot.com/']
    custom_settings = {
        'RETRY_TIMES': 100,
    }

    def parse (self, response):
      for href in response.xpath('//select[@id="BlogArchive1_ArchiveMenu"]/option/@value'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for href in response.xpath('//h3[@class="post-title entry-title"]/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_post)
    

    def parse_post(self, response):
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
          body = body + content.extract()
      except:
        body = ""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="post-body entry-content"]/descendant-or-self::a/@href'):
          extracted = href.extract()
          if ('http://autismsedges.blogspot.com' not in extracted) and ('http://technorati.com' not in extracted)and ('.jpg'!= extracted[-4:]):
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