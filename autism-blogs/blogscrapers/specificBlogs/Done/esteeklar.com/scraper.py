import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://www.esteeklar.com/']
    custom_settings = {
        'RETRY_TIMES': 10,
    }
    
    def parse (self, response):
      for href in response.xpath('//li[@id="archives-3"]/ul/li/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for postlink in response.xpath('//div[@class="post-title"]/h2/a/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      stringdate = response.url[25:35]
      
      try:
        title = response.xpath('//div[@class="post-title"]/h2/a/text()').extract()[0]
      except:
        title = ""

      body = ""
      for content in response.xpath('//div[@class="entry clear"]//*[not(descendant::ul[@class="socialwrap size24 row"]) and not(ancestor-or-self::ul[@class="socialwrap size24 row"])]/text()'):
        body = body + content.extract() + ' '
      
      

      outgoing_links = []
      for href in response.xpath('//div[@class="entry clear"]//*[not(descendant::ul[@class="socialwrap size24 row"]) and not(ancestor-or-self::ul[@class="socialwrap size24 row"])]/@href'):
        extracted = href.extract()
        if 'http://www.esteeklar.com' not in extracted:
          outgoing_links.append(extracted)
      


      yield {
          'date' : stringdate,
          'body' : body,
          'link': response.url,
          'title': title,
          'outgoing_links': outgoing_links
        }