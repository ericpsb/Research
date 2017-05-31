import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://mfamama.typepad.com/my-blog/archives.html']
    custom_settings = {
        'RETRY_TIMES': 10,
    }
    
    def parse (self, response):
      for href in response.xpath('//div[@class="archive-date-based archive"]/div/ul/li/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for href in response.xpath('//span[@class="pager-right"]/a/@href'):
        full_url = response.urljoin(href.extract())
        yield scrapy.Request(full_url, callback=self.parse_link)
      for postlink in response.xpath('//h3[@class="entry-header"]/a/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = response.xpath('//h2[@class="date-header"]/text()').extract()[0]
      except:
        stringdate=""

      try:
        title = response.xpath('//h3[@class="entry-header"]/text()').extract()[0]
      except:
        title = ""

      body = ""
      for content in response.xpath('//div[@class="entry-content"]/descendant-or-self::node()/text()'):
        body = body + content.extract() + ' '
      
      

      outgoing_links = []
      for href in response.xpath('//div[@class="entry-content"]/descendant-or-self::a/@href'):
        extracted = href.extract()
        if 'http://mfamama.typepad.com/my-blog' not in extracted:
          outgoing_links.append(extracted)
      
      yield {
          'date' : stringdate,
          'body' : body,
          'link': response.url,
          'title': title,
          'outgoing_links': outgoing_links
        }