import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['https://adiaryofamom.com/']
    custom_settings = {
        'RETRY_TIMES': 100,
    }
    
    def parse (self, response):
      for href in response.xpath('//aside[@id="archives-3"]/ul/li/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for href in response.xpath('//div[@class="nav-previous"]/a/@href'):
        full_url = response.urljoin(href.extract())
        yield scrapy.Request(full_url, callback=self.parse_link)
      for postlink in response.xpath('//h2[@class="entry-title"]/a/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = response.url[25:35]
      except:
        stringdate =""
      
      try:
        title = response.xpath('//h2[@class="entry-title"]/text()').extract()[0]
      except:
        title =""
      
      try:
        body = ""
        for content in response.xpath('//div[@class="storycontent"]/descendant-or-self::node()/text()'):
          body = body + content.extract() + ' '
      except:
        body = ""
      
      
      try:
        body = ""
        for content in response.xpath('//div[@class="entry-content"]//*[not(descendant::div[@id="jp-post-flair"]) and not(ancestor-or-self::div[@id="jp-post-flair"])]/text()'):
          body = body + content.extract() + ' ' + " "
      except:
        body =""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="entry-content"]//*[not(descendant::div[@id="jp-post-flair"]) and not(ancestor-or-self::div[@id="jp-post-flair"])]/@href'):
          extracted = href.extract()
          if 'https://adiaryofamom.com/' not in extracted:
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
