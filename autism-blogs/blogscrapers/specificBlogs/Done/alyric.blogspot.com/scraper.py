import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['http://alyric.blogspot.com/']
    custom_settings = {
        'RETRY_TIMES': 100,
    }
    
    def parse (self, response):
      for href in response.xpath('//ul[@class="archive-list"]/li/a/@href'):
          if href.extract() !="":
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_link)
    
    def parse_link(self, response):
      for postlink in response.xpath('//a[@class="comment-link"]/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = response.xpath('//h2[@class="date-header"]/text()').extract()[0]
        i = stringdate.index(',') + 1
        stringdate = stringdate[i:]
      except:
        stringdate = ""

      try:
        title = response.xpath('//h3[@class="post-title"]/text()').extract()[0]
      except:
        title =""

      try:
        body = ""
        for content in response.xpath('//div[@class="post-body"]/descendant-or-self::node()/text()'):
          body = body + content.extract() + ' '
      except:
        body =""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="post-body"]/descendant-or-self::node()/@href'):
          extracted = href.extract()
          if 'http://alyric.blogspot.com/' not in extracted:
            outgoing_links.append(extracted)
      except:
        outgoing_links = ""
      

      link = response.url
      index = link.find("#comments")
      if index != -1:
        link = link[:index]


      yield {
          'date' : stringdate,
          'body' : body,
          'link': link,
          'title': title,
          'outgoing_links': outgoing_links
        }