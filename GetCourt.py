# coding: utf-8
import re
import urllib.request
import MySQL
import UrlUtil
import json


class CourtUtil:
    def spider_and_upsert_court_info(self, court_list_url, court_item_regex, court_auction_count_url):
        print("start to get court list and insert into DB")
        court_info_list = self.get_court_data(court_list_url, court_item_regex)
        court_acution_count = self.get_court_auction_count(court_auction_count_url)
        for court_info in court_info_list:
            if court_info.__len__() > 1:
                court_id = court_info[0]
                court_name = court_info[1]
                auction_count = 0
                if court_id in court_acution_count.keys():
                    auction_count = int(court_acution_count[court_id])
                select_sql = 'select count(*) from Courts where CourtId=' + court_id
                insert_sql = 'insert into Courts (CourtId, CourtName, AuctionCount) values (' + court_id + ',"' + court_name + '",' + str(auction_count) + ')'
                update_sql = 'update Courts set AuctionCount= ' + str(auction_count) + ' where CourtId=' + court_id
                mysql.upsert(select_sql, insert_sql, update_sql)
        print("end to get court list and insert into DB")

    def get_court_data(self, court_list_url, court_item_regex):
        html = UrlUtil.get_html(court_list_url)
        court_data_list = re.findall(re.compile(court_item_regex, re.S), html.decode('utf8'))
        return court_data_list

    def get_court_auction_count(self, court_auction_count_url):
        court_auction_count_json = UrlUtil.get_json(court_auction_count_url)
        return court_auction_count_json['data']


if __name__ == '__main__':
    mysql = MySQL.MySQL('auction_spider_jd')
    court_util = CourtUtil()
    # court_util.spider_and_upsert_court_info('https://auction.jd.com/s/allCourtsList.html', r'<a href="\S*?=(\d+)" \S+>\s*"\s*(\S+)\s*"\s*</a>\s*</span>\s*<span class="counts" style="color: red;"> \((\d+)')
    court_util.spider_and_upsert_court_info('https://auction.jd.com/s/allCourtsList.html', r'<a href="\S*?=(\d+)" \S+>\s*(\S+)\s*<span class="counts" ></span>\s*', 'https://auction.jd.com/json/queryCourtAllProductCounts.do')
    court_list = mysql.get_courts()
    print(court_list)
