# -*- coding: utf-8 -*-
import re

import scrapy
import time

from Ali1688Spider.items import Ali1688SpiderItem

citys = ['广东', '浙江', '江苏', '山东', '河北', '河南', '福建', '辽宁', '安徽', '广西', '山西', '海南', '内蒙古', '吉林', '黑龙江', '湖北', '湖南', '江西',
         '宁夏', '新疆', '青海', '陕西', '甘肃', '四川', '云南', '贵州', '西藏', '台湾', '香港']
cityUrlcode = ['%B9%E3%B6%AB', '%D5%E3%BD%AD', '%BD%AD%CB%D5', '%C9%BD%B6%AB', '%BA%D3%B1%B1', '%BA%D3%C4%CF', '%B8%A3%BD%A8', '%C1%C9%C4%FE', '%B0%B2%BB%D5', '%B9%E3%CE%F7']

cityUrlcode1 = ['%B9%E3%B6%AB', '%D5%E3%BD%AD', '%BD%AD%CB%D5', '%C9%BD%B6%AB', '%BA%D3%B1%B1', '%BA%D3%C4%CF', '%B8%A3%BD%A8', '%C1%C9%C4%FE', '%B0%B2%BB%D5', '%B9%E3%CE%F7']

cityUrlcode2 = ['%B9%E3%B6%AB', '%D5%E3%BD%AD', '%BD%AD%CB%D5', '%C9%BD%B6%AB', '%BA%D3%B1%B1', '%BA%D3%C4%CF', '%B8%A3%BD%A8', '%C1%C9%C4%FE', '%B0%B2%BB%D5']

class SupplierSpiderSpider(scrapy.Spider):
    name = 'supplier_spider'
    # urlcommon = 'https://s.1688.com/company/company_search.htm?keywords='
    # start_urls = []
    # for i in range(0, len(cityUrlcode)):
    #     start_urls.insert(i, urlcommon + cityUrlcode[i])
    start_urls = ['https://s.1688.com/company/company_search.htm?keywords=%B9%E3%B6%AB']

    # 解析一级页面获取详情页链接
    def parse(self, response):
        companylist = response.xpath('//div[@id="sw_mod_searchlist"]/ul[@class="sm-company-list fd-clr"]/li')
        for item in companylist:
            detailBlock = item.xpath(
                './/div[@class="list-item-left"]//div[@class="wrap"]//div[@class="list-item-detail"]')
            detailurl = detailBlock.xpath('.//div[@class="detail-left"]//div[3]/a[contains(@href, "")]/@href').extract()
            yield scrapy.Request(detailurl[0], callback=self.parse_detail,meta={'detailurl': detailurl[0]})

        #爬取完当前所有item的详情页之后翻页
        total_page = response.xpath('//span[@class="total-page"]/text()').extract()[0]
        totalpage = re.sub("\D", "", total_page)
        cur_page = response.xpath('//span[@class="page-cur"]/text()').extract()[0]
        next_url = response.xpath('//a[@class="page-next"]/@href').extract_first()
        print("当前页面>>>第",cur_page+"页")
        if(int(cur_page)<int(totalpage)):
            print("翻页"*20)
            yield scrapy.Request(url=next_url,callback=self.parse)
        else:
            print("*********************当前省份爬取完毕**************************")

    # 解析详情页获取数据
    def parse_detail(self, response):
        detailurl = response.meta['detailurl']
        print("detailurl>>>",detailurl)
        companyTag = response.xpath('//h1[@class="company-name"]')
        # 公司名称
        companyName = self.getListWithDefault(companyTag.xpath('./span/text()').extract())[0]
        companyName = self.replaceSpace(companyName)
        # 诚信年限
        loyaltyYears = \
            self.getListWithDefault(companyTag.xpath('./a[@class="icon icon-chengxintong"]/text()').extract())[0]
        # 诚信等级
        loyaltyLevel = self.getListWithDefault(companyTag.xpath('./a[last()]/text()').extract())[0]

        contactTag = response.xpath('//div[@class="text company-contact"]')
        # 联系人  J_STRENGTH_CompanyContact
        global contactPerson, telephone, mobile
        contactPerson = contactTag.xpath(
            '//div[@id="J_COMMON_CompanyContact"]/span[@class="contact-info"]/text()').extract()  # self.getListWithDefault()[0]
        contactPerson = self.getContactPerson(contactPerson)
        # 有两种布局，ID不一样 如果一种没获取到数据换另一种
        if len(contactPerson) == 0:
            print('second contactPerson')
            contactPerson = \
                self.getListWithDefault(contactTag.xpath('//span[@id="J_STRENGTH_CompanyContact"]/text()').extract())[0]
            contactPerson = self.replaceSpace(contactPerson)
        # 固话
        telephone = \
            self.getListWithDefault(response.xpath('string(//span[@id="J_COMMON_CompanyInfoTelShow"])').extract())[0]
        telephone = self.replaceSpace(telephone)
        if len(telephone) == 0:
            print('second telephone')
            telephone = self.getListWithDefault(
                response.xpath('string(//span[@id="J_STRENGTH_CompanyInfoTelShow"])').extract())[0]
            telephone = self.replaceSpace(telephone)
        # 手机号码
        mobile = \
            self.getListWithDefault(response.xpath('string(//div[@id="J_COMMON_CompanyInfoPhoneShow"])').extract())[0]
        mobile = self.replaceSpace(mobile)
        if len(mobile) == 0:
            print('second mobile')
            mobile = \
                self.getListWithDefault(
                    response.xpath('string(//span[@id="J_STRENGTH_CompanyInfoPhoneShow"])').extract())[
                    0]
            mobile = self.replaceSpace(mobile)

        # 成交数
        translateNum = self.getListWithDefault(
            response.xpath('string(//div[@id="J_CompanyTradeCreditRecord"]/ul/li[1])').extract())[0]
        translateNum = self.replaceSpace(translateNum)
        # 累计买家数
        buyerNum = self.getListWithDefault(
            response.xpath('string(//div[@id="J_CompanyTradeCreditRecord"]/ul/li[2])').extract())[0]
        buyerNum = self.replaceSpace(buyerNum)
        # 注册时间
        registerTime = self.getListWithDefault(response.xpath(
            'string(//div[@class="info-bottom"]//div[@class="info-box info-right"]//table/tr[1])')).extract()[0]
        registerTime = self.replaceSpace(registerTime)
        # 注册资金
        registerMoney = self.getListWithDefault(response.xpath(
            'string(//div[@class="info-bottom"]//div[@class="info-box info-right"]//table/tr[2])').extract())[0]
        registerMoney = self.replaceSpace(registerMoney)
        # 运营范围
        operateArea = self.getListWithDefault(response.xpath(
            'string(//div[@class="info-bottom"]//div[@class="info-box info-right"]//table/tr[3])').extract())[0]
        operateArea = self.replaceSpace(operateArea)
        # 地址
        address = self.getListWithDefault(response.xpath(
            'string(//div[@class="info-bottom"]//div[@class="info-box info-right"]//table/tr[4])').extract())[0]
        address = self.replaceSpace(address).replace("查看地图", "")

        companyCode = self.getListWithDefault(
            response.xpath('string(//div[@class="register-data"]//table/tbody/tr[3])').extract())[0]
        companyCode = companyCode.replace("法定代表人：", "")
        companyCode = self.replaceSpace(companyCode).replace("\xa0", "")
        dataitem = Ali1688SpiderItem()
        dataitem['detailurl'] = detailurl
        dataitem['companyName'] = companyName
        dataitem['loyaltyYears'] = loyaltyYears
        dataitem['loyaltyLevel'] = loyaltyLevel
        dataitem['contactPerson'] = contactPerson
        dataitem['telephone'] = telephone
        dataitem['mobile'] = mobile
        dataitem['translateNum'] = translateNum
        dataitem['buyerNum'] = buyerNum
        dataitem['registerTime'] = registerTime
        dataitem['registerMoney'] = registerMoney
        dataitem['operateArea'] = operateArea
        dataitem['address'] = address
        dataitem['companyCode'] = companyCode
        baseInfo = {
            'companyName': companyName,
            'loyaltyYears': loyaltyYears,
            'loyaltyLevel': loyaltyLevel,
            'contactPerson': contactPerson,
            'telephone': telephone,
            'mobile': mobile,
            'translateNum': translateNum,
            'buyerNum': buyerNum,
            'registerTime': registerTime,
            'registerMoney': registerMoney,
            'operateArea': operateArea,
            'address': address,
            'companyCode': companyCode,
        }
        print(baseInfo)
        yield dataitem


    # 工具方法替换各种健
    def replaceSpace(self, params):
        if params is None:
            return "--"
        else:
            newstr = params.strip()
            newstr = newstr.replace(" ", "")
            newstr = newstr.replace("\r", "")
            newstr = newstr.replace("\n", "")
            newstr = newstr.replace("\t", "")
            return newstr

    # 工具方法给空的list返回默认值
    def getListWithDefault(self, mylist):
        if (isinstance(mylist, list)):
            if mylist:
                return mylist
            else:
                return mylist.insert(0, "no_data")
        else:
            print("mylist is not list>>>", mylist)
            return self.replaceSpace(mylist)

    def getContactPerson(self,name):
        if (isinstance(name, list)):
            if(len(name)== 0):
                return "联系人未知"
            else:
                return name[0]
        else:
            return name+""
