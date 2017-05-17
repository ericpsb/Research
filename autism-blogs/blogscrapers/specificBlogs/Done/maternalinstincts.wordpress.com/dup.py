import os
from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.request import request_fingerprint

class CustomFilter(RFPDupeFilter):

  def request_seen(self, request):
        if self.file:
            self.file.write(fp + os.linesep)