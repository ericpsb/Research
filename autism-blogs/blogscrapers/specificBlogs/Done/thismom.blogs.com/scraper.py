import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://thismom.blogs.com/']
    custom_settings = {
        'RETRY_TIMES': 100,
    }
    
    def parse (self, response):
      for href in response.xpath('//span[@class="pager-right"]/a/@href'):
        full_url = response.urljoin(href.extract())
        yield scrapy.Request(full_url, callback=self.parse)
      for href in response.xpath('//h3[@class="entry-header"]/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = response.xpath('//span[@class="post-footers"]/text()').extract()[0]
        if 'at' in stringdate:
          i = stringdate.index('at')
          stringdate = stringdate[:i]
        
      except:
        stringdate =""
      
      try:
        title = response.xpath('//h3[@class="entry-header"]/descendant-or-self::node()/text()').extract()[0]
      except:
        title =""

      body = ""
      for content in response.xpath('//div[@class="entry-body"]/descendant-or-self::node()/text()'):
        body = body + content.extract() + ' '
      
      

      outgoing_links = []
      for href in response.xpath('//div[@class="entry-body"]/descendant-or-self::a/@href'):
        extracted = href.extract()
        if 'http://thismom.blogs.com' not in extracted:
          outgoing_links.append(extracted)
      


      yield {
          'date' : stringdate,
          'body' : body,
          'link': response.url,
          'title': title,
          'outgoing_links': outgoing_links
        }