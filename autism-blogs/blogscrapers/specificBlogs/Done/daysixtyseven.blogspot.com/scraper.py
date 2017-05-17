import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://daysixtyseven.blogspot.com']
    custom_settings = {
        'RETRY_TIMES': 100,
    }
    
    def parse (self, response):
      for href in response.xpath('//select[@id="BlogArchive1_ArchiveMenu"]/option/@value'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for postlink in response.xpath('//h3[@class="post-title entry-title"]/a/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      stringdate = response.xpath('//h2[@class="date-header"]/span/text()').extract()[0]
      i = stringdate.find(',') + 2
      if i != 1:
          stringdate = stringdate[i:]

      title = response.xpath('//h3[@class="post-title entry-title"]/text()').extract()[0]
      

      body = ""
      for content in response.xpath('//div[@class="post-body entry-content"]/text() | //div[@class="post-body entry-content"]/descendant-or-self::node()/text()'):
        body = body + content.extract() + ' '
      
      

      outgoing_links = []
      for href in response.xpath('//div[@class="post-body entry-content"]/descendant-or-self::a/@href'):
        extracted = href.extract()
        if 'http://daysixtyseven.blogspot.com' not in extracted:
          outgoing_links.append(extracted)
      


      yield {
          'date' : stringdate,
          'body' : body,
          'link': response.url,
          'title': title,
          'outgoing_links': outgoing_links
        }