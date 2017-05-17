import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://noahsdad.com/']
    custom_settings = {
        'RETRY_TIMES': 10,
    }
    
    def parse (self, response):
      for href in response.xpath('//select[@id="archives-dropdown-3"]/option/@value'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for href in response.xpath('//li[@class="pagination-next"]/a/@href'):
        full_url = response.urljoin(href.extract())
        yield scrapy.Request(full_url, callback=self.parse_link)
      for postlink in response.xpath('//h2[@class="entry-title"]/a/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = ""
        for el in response.xpath('//span[@class="thread"]/descendant-or-self::node()/text()'):
          x = el.extract()
          d = {'Jan':'January', 'Feb':'February', 'Mar':'March', 'Apr':'April', 'Jun':'June', 'Jul':'July', 'Aug':'August', 'Sep':'September', 'Oct':'October', 'Nov':'November', 'Dec':'December'}
          if x in d:
            x = d[x]
          stringdate = stringdate + ","+ x
      except:
        stringdate = ""
      
      try:
        title = response.xpath('//h1[@class="entry-title"]/text()').extract()[0]
      except:
        title = ""

      body = ""
      for content in response.xpath('//div[@class="entry-content"]/*[not(self::div)]/descendant-or-self::node()/text()'):
        body = body + content.extract() + ' '
      
      

      outgoing_links = []
      for href in response.xpath('//div[@class="entry-content"]/*[not(self::div)]/descendant-or-self::node()/@href'):
        extracted = href.extract()
        if 'http://noahsdad.com' not in extracted:
          outgoing_links.append(extracted)
          
      yield {
          'date' : stringdate,
          'body' : body,
          'link': response.url,
          'title': title,
          'outgoing_links': outgoing_links
        }