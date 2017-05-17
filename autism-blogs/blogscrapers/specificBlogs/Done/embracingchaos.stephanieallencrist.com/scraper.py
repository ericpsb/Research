import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://embracingchaos.stephanieallencrist.com/']
    custom_settings = {
        'RETRY_TIMES': 10,
    }
    
    def parse (self, response):
      for href in response.xpath('//select[@id="archives-dropdown-3"]/option/@value'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for href in response.xpath('//li[@class="next"]/a/@href'):
        full_url = response.urljoin(href.extract())
        yield scrapy.Request(full_url, callback=self.parse_link)
      for postlink in response.xpath('//h2[@class="post-title"]/a/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      stringdate = response.xpath('//ul[@class="meta"]/li/text()').extract()[0]
      i = stringdate.find('at')-1
      stringdate = stringdate[10:i]
      title = response.xpath('//h2[@class="post-title"]/a/descendant-or-self::node()/text()').extract()[0]
      

      body = ""
      for content in response.xpath('//div[@class="storycontent"]/descendant-or-self::node()/text()'):
        body = body + content.extract() + ' '
      
      

      outgoing_links = []
      for href in response.xpath('//div[@class="storycontent"]/descendant-or-self::a/@href'):
        extracted = href.extract()
        if 'http://embracingchaos.stephanieallencrist.com' not in extracted:
          outgoing_links.append(extracted)
      


      yield {
          'date' : stringdate,
          'body' : body,
          'link': response.url,
          'title': title,
          'outgoing_links': outgoing_links
        }