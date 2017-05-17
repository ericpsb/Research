import scrapy

class test_spider(scrapy.Spider):
    name = "scraper"
    start_urls = ['https://juststimming.wordpress.com/', 'https://juststimming.wordpress.com/page/2/' , 'https://juststimming.wordpress.com/page/3/' , 'https://juststimming.wordpress.com/page/4/', 'https://juststimming.wordpress.com/page/5/']
    custom_settings = {
        'RETRY_TIMES': 10,
    }
    
    def parse(self, response):
      for postlink in response.xpath('//div[@id="content"]/div/h2/a/@href'):
         full_url = response.urljoin(postlink.extract())
         yield scrapy.Request(full_url, callback=self.parse_post)

    def parse_post(self, response):
      try:
        stringdate = response.xpath('//div[@class="signature"]/p[2]/text()').extract()[0]
        i = stringdate.find("at") -1 
        stringdate = stringdate[:i]
      except:
        stringdate = ""

      try:
        title = response.xpath('//div[@id="content"]/div/h2/text()').extract()[0]
      except:
        title =""

      try:
        body = ""
        for content in response.xpath('//div[@class="main"]//*[not(descendant::div[@class="sharedaddy sd-like-enabled sd-sharing-enabled"]) and not(ancestor-or-self::div[@class="sharedaddy sd-like-enabled sd-sharing-enabled"]) and not(descendant::div[@class="wpcnt"]) and not(ancestor-or-self::div[@class="wpcnt"])]/text()'):
          body = body + content.extract() + ' '
      except:
        body =""
      
      try:
        outgoing_links = []
        for href in response.xpath('//div[@class="main"]//*[not(descendant::div[@class="sharedaddy sd-like-enabled sd-sharing-enabled"]) and not(ancestor-or-self::div[@class="sharedaddy sd-like-enabled sd-sharing-enabled"])]/@href'):
          extracted = href.extract()
          if 'https://juststimming.wordpress.com' not in extracted and "https://wordpress.com/about-these-ads/" not in extracted:
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