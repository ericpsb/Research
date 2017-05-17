import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://www.donnathomson.com/']
    custom_settings = {
        'RETRY_TIMES': 10,
    }
    
    def parse (self, response):
      for href in response.xpath('//span[@id="blog-pager-older-link"]/a/@href'):
        full_url = response.urljoin(href.extract())
        yield scrapy.Request(full_url, callback=self.parse)
      for href in response.xpath('//h3[@class="post-title entry-title"]/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = response.xpath('//h2[@class="date-header"]/span/text()').extract()[0]
      except:
        stringdate =""
      
      try:
        title = response.xpath('//h2[@class="post-title entry-title"]/descendant-or-self::node()/text()').extract()[0]
      except:
        title =""

      body = ""
      for content in response.xpath('//div[@class="post-body entry-content"]/descendant-or-self::node()/text()'):
        body = body + content.extract() + ' '
      
      

      outgoing_links = []
      for href in response.xpath('//div[@class="post-body entry-content"]/descendant-or-self::a/@href'):
        extracted = href.extract()
        if 'http://www.donnathomson.com' not in extracted:
          outgoing_links.append(extracted)
      


      yield {
          'date' : stringdate,
          'body' : body,
          'link': response.url,
          'title': title,
          'outgoing_links': outgoing_links
        }