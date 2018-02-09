import requests
import re
import time
import xlrd
import json
import pymongo
from lxml import html

url = 'https://www.zhipin.com/job_detail/1416961389.html?ka=search_list_1'
url2 = 'https://www.zhipin.com/job_detail/1416743560.html'
base_url = 'https://www.zhipin.com/c101020100/s_301-b_%E9%97%B5%E8%A1%8C%E5%8C%BA-h_101020100-t_801/?page={num}&ka=page-{num}'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
cookies = {
    'Cookie': '__c=1515999644; lastCity=101020100; JSESSIONID=""; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1515999646; __l=r=&l=%2F; toUrl=https%3A%2F%2Fwww.zhipin.com%2Fjob_detail%2F1416961389.html%3Fka%3Dsearch_list_1; __a=52065629.1515999644.1515999649.1515999644.34.3.32.34; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1516962048'}
file_path = 'boss_recruit_浦东_未融资_天使轮_A轮_99_url.xlsx'
session = requests.session()
db = pymongo.MongoClient(host='localhost', port=27017)['Falonie']
collection = db['boss_recruit_上海_jobs_supplement']
collection_url = db['boss_recruit_闵行_天使轮_filter']
collection_filter = db['boss_recruit_上海_supplement_urls2']
collection_filter_duplicates_url = db['boss_recruit_闵行_天使轮_filter']


def read_excel(file):
    with xlrd.open_workbook(file) as data_:
        table = data_.sheets()[0]
        url_list = [table.row_values(rownum)[0] for rownum in range(206, table.nrows)]
        return url_list


def read_excel_(file):
    with xlrd.open_workbook(file) as data_:
        table = data_.sheets()[0]
        for rownum in range(347, table.nrows):
            url = table.row_values(rownum)[0]
            yield url


def read_mongodb():
    url = [_['url'] for _ in collection_filter.find({})]
    return url


def proxy():
    time.sleep(15)
    proxy_api_url = 'http://api.xdaili.cn/xdaili-api//privateProxy/getDynamicIP/DD20181265614RYXDKJ/03df84e21ddb11e79ff07cd30abda612?returnType=2'
    res = requests.get(proxy_api_url, timeout=50)
    content = res.content.decode()
    print(content)
    ipdict = json.loads(content)
    print(ipdict)
    ip = ipdict.get('RESULT')
    ip_address = 'http://' + ip.get('wanIp') + ':' + ip.get('proxyport')
    proxy = {
        'http': ip_address,
        'https': ip_address
    }
    return proxy


def parse_page(url, proxies=None):
    # proxies = proxy()
    r = session.get(url=url, headers=headers, cookies=cookies, proxies=proxies, timeout=50).text
    selector = html.fromstring(r)
    item = {}
    for _ in selector.xpath('//div[@class="job-primary detail-box"]/div[@class="info-primary"]'):
        release_time = _.xpath('div[@class="job-author"]/span/text()')
        item['release_time'] = ''.join(str(i) for i in release_time)
        position = _.xpath('div[@class="name"]/text()')
        item['position'] = ''.join(str(i) for i in position)
    for _ in selector.xpath('//div[@class="info-company"]'):
        company = _.xpath('h3/a/text()')
        item['company'] = ''.join(str(i) for i in company)
        try:
            item['rounds'], item['scale'], item['homepage'] = _.xpath('p/text()')
        except Exception:
            item['rounds'] = ','.join(str(i).strip() for i in _.xpath('p/text()'))
        industry = _.xpath('p/a/text()')
        item['industry'] = ''.join(str(i).strip() for i in industry)
    for _ in selector.xpath('//div[@class="job-detail"]'):
        recruiter = _.xpath('div[@class="detail-op"]/h2/text()')
        item['recruiter'] = ''.join(str(i) for i in recruiter)
        recruiter_title = _.xpath('div[@class="detail-op"]/p/text()')
        item['recruiter_title'] = ''.join(str(i) for i in recruiter_title)
    for _ in selector.xpath('//div[@class="job-detail"]/div[@class="detail-content"]'):
        company_info = _.xpath('div[@class="job-sec company-info"]/descendant::text()')
        item['company_info'] = re.sub(r'[\n\xa0\t\s ]', '', ''.join(str(i).strip() for i in company_info))
        job_description = _.xpath('div[1]/descendant::text()')
        item['job_description'] = re.sub(r'[\n\xa0\t\s ]', '', ''.join(str(i).strip() for i in job_description))
        # business_info_company = _.xpath('div[4]/div[@class="name"]/text()|div[2]/div[@class="name"]/text()|div[3]/div[@class="name"]/text()')
        business_info_company = _.xpath('div/div[@class="name"]/text()')
        item['business_info_company'] = ''.join(str(i).strip() for i in business_info_company)
        work_location = _.xpath('div[5]/h3/text()|div/div[@class="job-location"]/div[@class="location-address"]/text()')
        item['work_location'] = ''.join(str(i).strip() for i in work_location)
        item['url'] = url
    # print(item)
    collection.insert(item)
    return item


def extract_url(url, proxies):
    r = session.get(url=url, headers=headers, cookies=cookies, proxies=proxies).text
    selector = html.fromstring(r)
    href_list = []
    for _ in selector.xpath('//div[@class="job-list"]/ul/li'):
        href = _.xpath('div/div[1]/h3/a/@href')
        if href:
            url = 'https://www.zhipin.com{}'.format(href[0])
            href_list.append({'url': url})
    collection.insert_many(href_list)
    return href_list


def main_excel():
    p = proxy()
    for i, _ in enumerate(read_excel_(file_path), 1):
        print(i, _)
        time.sleep(2)
        try:
            item = parse_page(_, p)
            if item.get('company') != None:
                print(item)
            elif item.get('company') == None:
                p = proxy()
                print(p)
                item = parse_page(_, p)
                print(item)
        except TimeoutError as e:
            print(e)
            p = proxy()
            continue
        except Exception as e:
            print(e)
            p = proxy()
            continue


def main_mongodb():
    p = proxy()
    for i, _ in enumerate(read_mongodb(), 1):
        url = _
        print(i, url)
        time.sleep(.2)
        try:
            item = parse_page(url, p)
            if item.get('company') != None:
                print(item)
            elif item.get('company') == None:
                p = proxy()
                print(p)
                item = parse_page(url, p)
                print(item)
        except TimeoutError as e:
            print(e)
            p = proxy()
            continue
        except Exception as e:
            print(e)
            p = proxy()
            continue


if __name__ == '__main__':
    # print(extract_url(url2))
    # print(parse_page(url2))
    # print(parse_page(url2,proxy()))
    # print(read_excel(file_path).__len__())
    # print(list(read_excel_(file_path)).__len__())
    # print(proxy())
    # p=proxy()
    # time.sleep(10)
    # print(extract_url(url3,p))
    # extract_url_main()
    # main_excel()
    main_mongodb()
    # print(read_mongodb().__len__())
    pass
