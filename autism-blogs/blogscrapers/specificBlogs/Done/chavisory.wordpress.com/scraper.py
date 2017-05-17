import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['https://chavisory.wordpress.com/']
    custom_settings = {
        'RETRY_TIMES': 10,
    }
    
    def parse (self, response):
      for href in response.xpath('//li[@id="archives-4"]/ul/li/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for postlink in response.xpath('//h2[@class="storytitle"]/a/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = response.xpath('//h1[@class="storydate"]/text()').extract()[0]
      except:
        stringdate = ""

      try:
        title = response.xpath('//h2[@class="storytitle"]/text()').extract()[0]
      except:
        title =""

      try:
        body = ""
        for content in response.xpath('//div[@id="content"]/div/p[not(@*)]/descendant-or-self::node()/text()'):
          body = body + content.extract() + ' '
      except:
        body =""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@id="content"]/div/p[not(@*)]/descendant-or-self::node()/@href'):
          extracted = href.extract()
          if 'https://chavisory.wordpress.com' not in extracted:
            outgoing_links.append(extracted)
      except:
        outgoing_links = ""
      


      yield {
          'date' : stringdate,
          'body' : body,
          'link': response.url,
          'title': title,
          'outgoing_links': outgoing_links
        }