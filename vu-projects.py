#!/usr/bin/python3

from scrapy.crawler import CrawlerProcess

import scrapy
import json
import os
import urllib
import shutil
import sys

try:
    import params
except ImportError:
    print("Please create params.py based on params_default.py first.")
    sys.exit(1)


class VUPSpider(scrapy.Spider):
    name = 'vuprojects'
    firstReport = True

    start_urls = [
        params.projects_url + params.username,
    ]

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formxpath='//form[@id="loginForm"]',
            formdata={
                'UserName': 'vu\\' + params.username,
                'Password': params.password,
                'AuthMethod': 'FormsAuthentication',
            },
            callback=self.after_login)

    def after_login(self, response):
        jsonresponse = json.loads(response.text)
        for record in jsonresponse:
            reportUrl = params.reports_url + \
                params.username + '/' + record['Guid']
            reportUrl += '?' + urllib.parse.urlencode(record)
            yield scrapy.Request(url=reportUrl, callback=self.download_report)

    def download_report(self, response):
        parsed_url = urllib.parse.urlparse(response.url)
        record = urllib.parse.parse_qs(parsed_url.query)

        file = params.report_file.format(
            Guid=record['Guid'][0],
            ProjectId=record['ProjectId'][0].replace(
                '/', ''),
            ProjectDescription=record['ProjectDescription'][0]
        )
        file = os.path.join(params.storage_dir, file)
        print('{url} -> {file}'.format(url=response.url, file=file))

        if self.firstReport:
            if params.storage_dir_cleanup and os.path.exists(params.storage_dir):
                shutil.rmtree(params.storage_dir)
            if not os.path.exists(params.storage_dir):
                os.makedirs(params.storage_dir)
            self.firstReport = False

        with open(file, 'wb+') as f:
            f.write(response.body)


#
# main()
#
c = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0',
})
c.crawl(VUPSpider)
c.start()
