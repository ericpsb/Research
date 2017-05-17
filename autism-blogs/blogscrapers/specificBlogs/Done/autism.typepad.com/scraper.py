import scrapy

class test_spider(scrapy.Spider):
    name = "scraperd"
    start_urls = ['http://autism.typepad.com/autism/archives.html']
    custom_settings = {
        'RETRY_TIMES': 10,
    }
    
    def parse (self, response):
      for href in response.xpath('//div[@class="archive-date-based archive"]/div/ul/li/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for href in response.xpath('//div[@class="pager-bottom pager-entries pager content-nav"]/div/a/@href'):
        full_url = response.urljoin(href.extract())
        yield scrapy.Request(full_url, callback=self.parse_link)
      for postlink in response.xpath('//span[@class="excerpt-more-link"]/a/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = response.xpath('//span[@class="entry-date"]/a/text()').extract()[0]
      except:
        stringdate =""
      
      try:
        title = response.xpath('//span[@class="entry-title"]/a/text()').extract()[0]
      except:
        title = ""

      try:
        body = ""
        for content in response.xpath('//div[@class="entry-body font-entrybody"]/descendant-or-self::node()/text()'):
          body = body + content.extract() + ' '
      except:
        body =""
      
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="entry-body font-entrybody"]/descendant-or-self::a/@href'):
          extracted = href.extract()
          if 'http://autism.typepad.com/' not in extracted:
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



