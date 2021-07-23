#!/usr/bin/python3

from scrapy.crawler import CrawlerProcess
from scrapy import signals
from zipfile import ZipFile
from datetime import datetime

import scrapy
import json
import os
import urllib
import shutil
import sys
import uuid
import zipfile
import logging
import traceback
import getpass
import paramiko

try:
    import params
except ImportError:
    print("Please create params.py based on params_default.py first.")
    sys.exit(1)


class VUPSpider(scrapy.Spider):
    name = 'vuprojects'
    firstReport = True
    zip_obj = None

    start_urls = [
        params.projects_url + params.username,
    ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed,
                                signal=signals.spider_closed)
        spider.logger.setLevel(params.log_level)

        if params.password == '{prompt}':
            params.password = getpass.getpass(
                prompt='Enter your password: ')
        if params.upload_password == '{prompt}':
            params.upload_password = getpass.getpass(
                prompt='Enter your upload_password: ')
        elif params.upload_password == '{password}':
            params.upload_password = params.password

        return spider

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
        logger = self.logger
        parsed_url = urllib.parse.urlparse(response.url)
        record = urllib.parse.parse_qs(parsed_url.query)

        filebase = params.report_file.format(
            Guid=record['Guid'][0],
            ProjectId=record['ProjectId'][0].replace(
                '/', ''),
            ProjectDescription=record['ProjectDescription'][0]
        )
        file = os.path.join(params.storage_dir, filebase)
        logger.info('Downloading {url} -> {file}'.format(url=response.url, file=file))

        if self.firstReport:
            if params.storage_dir_cleanup and os.path.exists(params.storage_dir):
                shutil.rmtree(params.storage_dir)
            if not os.path.exists(params.storage_dir):
                os.makedirs(params.storage_dir)
            if params.report_zip_file:
                zip_filebase = params.report_zip_file.format(
                    username=params.username,
                    date=datetime.now().isoformat().replace(':', '-'),
                    date_min=datetime.now().isoformat(timespec='minutes').replace(':', '-'),
                    date_sec=datetime.now().isoformat(timespec='seconds').replace(':', '-'),
                    date_ms=datetime.now().isoformat(timespec='milliseconds').replace(':', '-'),
                    uuid=uuid.uuid4()
                )
                zip_file = os.path.join(params.storage_dir, zip_filebase)
                self.zip_obj = ZipFile(zip_file, 'a',
                                       compression=zipfile.ZIP_DEFLATED)
            self.firstReport = False

        with open(file, 'wb+') as f:
            f.write(response.body)
        if self.zip_obj:
            self.zip_obj.write(file, arcname=filebase)

    def spider_closed(self, spider):
        if self.zip_obj:
            self.zip_obj.close()
        if params.upload_hostname:
            self.upload(self.zip_obj.filename)

    def upload(self, local_file):
        logger = logging.getLogger('paramiko')
        logger.setLevel(params.log_level)

        # Open hostkey file
        hostkey_file = None
        hostkey = None
        hostname = params.upload_hostname
        try:
            hostkey_file = os.path.expanduser(
                os.path.join('~', '.ssh', 'known_hosts'))
            if not os.path.isfile(hostkey_file):
                hostkey_file = os.path.expanduser(
                    os.path.join('~', 'ssh', 'known_hosts'))
            host_keys = paramiko.util.load_host_keys(hostkey_file)
        except IOError:
            logger.error('Unable to open host keys file')
            sys.exit(1)
        logger.info('Using host key file %s' % hostkey_file)

        # Locate hostkey for hostname
        if hostname not in host_keys:
            logger.error('Host name not in host keys file, ssh manually first')
            sys.exit(1)
        hostkeytype = host_keys[hostname].keys()[0]
        hostkey = host_keys[hostname][hostkeytype]
        logger.info('Using host key of type %s' % hostkeytype)

        # Connect to hostname and upload file
        try:
            t = paramiko.Transport((hostname, params.upload_ssh_port))
            t.connect(hostkey, params.upload_username,
                      params.upload_password)
            sftp = paramiko.SFTPClient.from_transport(t)
            basefile = os.path.basename(local_file)
            remote_file = params.upload_hostdir + '/' + basefile
            logger.info('Uploading localhost:{local} -> {h}:{remote}'.format(
                local=local_file, h=hostname, remote=remote_file))
            sftp.put(local_file, remote_file)
            t.close()
        except Exception as e:
            logger.error('Caught exception: %s: %s' % (e.__class__, e))
            traceback.print_exc()
            try:
                t.close()
            except:
                pass
            sys.exit(1)


#
# main()
#
c = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0',
})
c.crawl(VUPSpider)
c.start()
