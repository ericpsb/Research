import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://extraordinary-ordinary.net/archives/']
    custom_settings = {
        'RETRY_TIMES': 10,
    }
    
    def parse (self, response):
      for href in response.xpath('//div[@class="archivel"]/ul[2]/li/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for postlink in response.xpath('//h2[@class="entry-title"]/a/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = response.xpath('//p[@class="headline_meta"]/*/text()').extract()[0]
      except:
      	stringdate = ""

      try:
        title = response.xpath('//h1[@class="entry-title"]/text()').extract()[0]
      except:
      	title =""

      try:
        body = ""
        for content in response.xpath('//div[@class="format_text entry-content"]/descendant-or-self::node()/text()'):
          body = body + content.extract() + ' '
      except:
      	body =""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="format_text entry-content"]//*[not(descendant::div[@class="mr_social_sharing_wrapper"]) and not(ancestor-or-self::div[@class="mr_social_sharing_wrapper"])]/@href'):
          extracted = href.extract()
          if 'http://extraordinary-ordinary.net' not in extracted:
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