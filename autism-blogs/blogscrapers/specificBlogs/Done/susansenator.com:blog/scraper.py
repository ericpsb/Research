import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://susansenator.com/blog/']
    custom_settings = {
        'RETRY_TIMES': 10,
    }
    
    def parse (self, response):
      for href in response.xpath('//div[@id="NavBar2"]/ul[2]/li/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for link in response.xpath('//div[@id="Content"]/a/text()'):
          if "O" in link.extract() or "O" in link.extract()[0]:
            href = response.xpath('//div[@id="Content"]/a/@href')[0]
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
      for postlink in response.xpath('//h4[@class="blogItemTitle"]/a/@href'):
           full_url = response.urljoin(postlink.extract())
           yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = response.xpath('//h5[@class="blogDateHeader"]/text()').extract()[0]
      except:
        stringdate=""

      try:
        title = response.xpath('//h4[@class="blogItemTitle"]/a/text()').extract()[0]
      except:
        title = ""

      body = ""
      for content in response.xpath('//div[@class="blogPost"]'+
                '//*[not(descendant::div[@class="byline"])'+
                ' and not(ancestor-or-self::div[@class="byline"])]/text()'):
        body = body + content.extract() + ' '
      
      

      outgoing_links = []
      for href in response.xpath('//div[@class="blogPost"]'+
                '//*[not(descendant::div[@class="byline"])'+
                ' and not(ancestor-or-self::div[@class="byline"])]/@href'):
        extracted = href.extract()
        if 'http://susansenator.com/blog' not in extracted:
          outgoing_links.append(extracted)
      
      yield {
          'date' : stringdate,
          'body' : body,
          'link': response.url,
          'title': title,
          'outgoing_links': outgoing_links
        }