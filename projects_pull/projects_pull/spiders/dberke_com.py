# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from urlparse import urlparse
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
from shutil import copyfile

import json, re, sys, time, os, requests, urllib

from ..download import download

class MySpider(Spider):

    name = "dberke_com"    
    firm_name = "DEBORAH BERKE PARTNERS"

    start_urls = [
                    'http://www.dberke.com/work'
                    ]

    def parse(self, response):
        projects = response.xpath('//section[contains(@class, "project_image_list")]/div/a')
        
        for project in projects:
            detail = {}            
            year = project.xpath('./p/span[@class="date"]/text()').extract()
            
            if "progress" in year:
                year = "2019"
            
            detail['project_year'] = year
            yield Request(response.urljoin(project.xpath('./@href').extract_first()), self.parse_project, meta={'detail':detail})
            
            
    
    def parse_project(self, response):
        
        item = OrderedDict()
        
        item['Src'] = response.url
        item['Project Name'] = response.xpath('//h1/span[@class="name"]/text()').extract_first()
        item['Project Short'] = ''
        item['Project Description'] = ' '.join(response.xpath('//header/following-sibling::p[1]/text()').extract())
        item['Project Location'] = ' '.join(response.xpath('//h1/span[@class="location"]/text()').extract()).strip('\n')
        item['Project Year'] = response.meta['detail']['project_year']
        categories = response.xpath('//section[contains(@class, "story_holder")]//nav/ul/li//a/text()').extract()
        item['Project Type'] = categories[0]
        item['Work Type'] = ','.join(categories[1:])
        item['Firm Name'] = self.firm_name
        item['Specific Designer Name(s)'] = response.xpath('//strong[text()="Key People"]/following-sibling::a/text()').extract()
        item['Photo Credit'] = self.firm_name
        item['Images'] = []

        images = response.xpath('//*[@class="items images_holder columns span_six clear"]//img/@src').extract()
        print (images)
        for idx, img in enumerate(images):
            filename = self.get_image_filename(item['Project Name'])
            download(response.urljoin(img), "images/{}/{}".format(self.firm_name, filename+str(idx+1)+".jpg"))
            item['Images'].append(filename+str(idx+1)+".jpg")        

        yield item

    def get_image_filename(self, project_name):
        name = self.firm_name.lower().replace(" & ", " ").replace(" ","") + "-"
        name += project_name.lower().replace(" ", "-")

        return name