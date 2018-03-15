from scrapy.http import  Request, FormRequest
from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from SCOI.items import *
import re
import requests
import json
import urllib 

class SCOI(BaseSpider):
    name = 'SCOI_browse'
    start_urls = ['http://www.supremecourtofindia.nic.in/case-status']
    def __init__(self,party_name = '', party_year = '', party_status = '', **kwargs):
        super(SCOI, self).__init__(**kwargs)
        self.party_name = party_name
        self.party_year = party_year
        self.party_status = party_status

        self.data = [ 
          ('PartyType', ''),
          ('PartyName', self.party_name), 
          ('PartyYear', self.party_year), 
          ('PartyStatus', self.party_status),
          ('page', '1'),
        ]

    def parse(self, response):
        yield FormRequest('http://www.supremecourtofindia.nic.in/php/getPartyDetails.php', callback=self.parse_next, formdata = self.data)

    def parse_next(self, response):
        sel = Selector(response)
        case_urls = sel.xpath('//a[@class="colorbox-inline"]/@href').extract()
        for case_url in case_urls:
            case_url = 'http://www.supremecourtofindia.nic.in/'+ case_url
            yield Request(case_url, callback = self.parse_case_url)
        next_page = ''.join(sel.xpath('//li[@class="active"][contains(text(), "Next")]/@p').extract()).strip()
        if next_page:
            self.data.pop()
            page = ('page', '%s' %next_page)
            self.data.append(page)
            print self.data
            yield FormRequest('http://www.supremecourtofindia.nic.in/php/getPartyDetails.php', callback=self.parse_next, formdata = self.data)
            
    def parse_case_url(self, response):
        sel = Selector(response)
        records = sel.xpath('//div[h4[a[contains(text(),"Case Details")]]]/following-sibling::div')
        diary_no = ' '.join(records.xpath('.//tr[td[contains(text(), "Diary No.")]]//td[not(@*)]//text()').extract()).encode('utf-8')
        diary_no = diary_no.replace('\xc2\xa0\xc2\xa0','')
        case_no = ' '.join(records.xpath('.//tr[td[contains(text(), "Case No.")]]//td[not(@*)]//text()').extract()).encode('utf-8')
        case_no = case_no.replace('\xc2\xa0\xc2\xa0','')
        present_last = ' '.join(records.xpath('.//tr[td[contains(text(), "Present/Last Listed On")]]//text()').extract()).encode('utf-8')
        present_last = present_last.replace('\n','')
        status = ' '.join(records.xpath('.//tr[td[contains(text(), "Status/Stage")]]//text()').extract()).encode('utf-8')
        status = status.replace('\n','')
        listed_on = ' '.join(records.xpath('.//tr[td[contains(text(), "Tentatively case may be listed on ")]]//text()').extract()).encode('utf-8')
        listed_on = listed_on.replace('\n','')
        admitted = ' '.join(records.xpath('.//tr[td[contains(text(), "Admitted")]]//text()').extract()).encode('utf-8')
        category =' '.join(records.xpath('.//tr[td[contains(text(), "Category")]]//td[not(@*)]//text()').extract()).encode('utf-8')
        act = ' '.join(records.xpath('.//tr[td[contains(text(), "Act")]]//td[not(@*)]//text()').extract()).encode('utf-8')
        petitioner = ' '.join(records.xpath('.//tr[td[contains(text(), "Petitioner(s)")]]//td[not(@*)]//text()').extract()).encode('utf-8')
        petitioner = petitioner.replace('\xc2\xa0\xc2\xa01','').replace('\xc2\xa0\xc2\xa0','')
        respondent = ' '.join(records.xpath('.//tr[td[contains(text(), "Respondent(s)")]]//td[not(@*)]//text()').extract()).encode('utf-8')
        respondent = respondent.replace('\xc2\xa0\xc2\xa01','').replace('\xc2\xa0\xc2\xa050','').replace('\xc2\xa0\xc2\xa02','').replace('\xc2\xa0\xc2\xa0','').replace('\xc2\xa0\xc2\xa03','').replace('\xc2\xa0\xc2\xa0','')
        pet_advocate = ' '.join(records.xpath('.//tr[td[contains(text(), "Pet. Advocate(s)")]]//td[not(@*)]//text()').extract()).encode('utf-8')
        pet_advocate = pet_advocate.replace('\xc2\xa0\xc2\xa0','')
        resp_advocate   = ' '.join(records.xpath('.//tr[td[contains(text(), "Resp. Advocate(s)")]]//td[not(@*)]//text()').extract()).encode('utf-8')
        u_section = ' '.join(records.xpath('.//tr[td[contains(text(), "U/Section")]]//td[not(@*)]//text()').extract()).encode('utf-8')
        SCOI = SCOIItem()
        SCOI['diary_no'] = diary_no 
        SCOI['case_no'] = case_no 
        SCOI['present_last'] = present_last 
        SCOI['status'] = status 
        SCOI['listed_on'] = listed_on 
        SCOI['admitted'] = admitted 
        SCOI['category'] = category 
        SCOI['act'] = act 
        SCOI['petitioner'] = petitioner 
        SCOI['respondent'] = respondent 
        SCOI['pet_advocate'] = pet_advocate 
        SCOI['resp_advocate'] = resp_advocate 
        SCOI['u_section'] = u_section 
        yield SCOI

