# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from urlparse import urlparse
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
from shutil import copyfile

import json, re, sys, time, os, requests, urllib

from ..download import download

class MySpider(Spider):

    name = "haririandhariri_com"    
    firm_name = "Hariri & Hariri Architecture"

    start_urls = ['http://www.haririandhariri.com/projects',]

    def parse(self, response):
        projects = response.xpath('//a[@class="project"]')
        
        for project in projects:
            details = project.xpath('./div/div[2]//text()').extract()
            detail = {}
            detail['project_name'] = details[len(details) - 1 - 2]
            detail['project_location'] = details[len(details) - 1 - 1]
            detail['project_year'] = details[len(details) - 1]
                        
            if len(details) < 3:
                continue

            link = project.xpath('./@href').extract_first()
            
            yield Request(response.urljoin(link), self.parse_project, meta={'detail':detail})
            
    
    def parse_project(self, response):
        
        item = OrderedDict()

        descriptions = response.xpath('//*[@class="sqs-block-content"]/p/text()').extract()
        
        item['Src'] = response.url
        item['Project Name'] = response.meta['detail']['project_name']
        item['Project Short'] = descriptions[0]
        item['Project Description'] = ' '.join(descriptions[1:])
        item['Project Location'] = response.meta['detail']['project_location']
        item['Project Year'] = response.meta['detail']['project_year']
        item['Project Type'] = ''
        item['Work Type'] = ''
        item['Firm Name'] = self.firm_name
        item['Specific Designer Name(s)'] = ''
        item['Photo Credit'] = self.firm_name
        item['Images'] = []

        images = response.xpath('//img[@class="thumb-image"]/@data-src').extract()
        print images
        for idx, img in enumerate(images):
            filename = self.get_image_filename(item['Project Name'])
            download(img, "images/{}/{}".format(self.firm_name, filename+str(idx+1)+".jpg"))
            item['Images'].append(filename+str(idx+1)+".jpg")
        

        yield item

    def get_image_filename(self, project_name):
        name = self.firm_name.lower().replace(" & ", " ").replace(" ","") + "-"
        name += project_name.lower().replace(" ", "-")

        return name