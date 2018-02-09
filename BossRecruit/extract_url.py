import requests
import pymongo
import time
import json
import re
from lxml import html

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
cookies = {
    'Cookie': '__c=1515999644; lastCity=101020100; JSESSIONID=""; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1515999646; __l=r=&l=%2F; toUrl=https%3A%2F%2Fwww.zhipin.com%2Fjob_detail%2F1416961389.html%3Fka%3Dsearch_list_1; __a=52065629.1515999644.1515999649.1515999644.34.3.32.34; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1516962048'}
db = pymongo.MongoClient(host='localhost', port=27017)['Falonie']
collection = db['boss_recruit_徐汇_jobs']
collection_url = db['boss_recruit_上海_supplement_urls']
collection_uncrawled_url = db['boss_recruit_徐汇_uncrawled_urls']
session = requests.session()
base_url='https://www.zhipin.com/c101020100/s_30{scale}-b_崇明县-h_101020100-t_80{rounds}/?page={page_num}&ka=page-{page_num}'

def read_mongodb():
    urls = [_['url'] for _ in collection_url.find({})]
    return urls


def proxy():
    time.sleep(15)
    proxy_api_url = 'http://api.xdaili.cn/xdaili-api//privateProxy/getDynamicIP/DD20181265614RYXDKJ/03df84e21ddb11e79ff07cd30abda612?returnType=2'
    res = requests.get(url=proxy_api_url, timeout=50)
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


def generate_url():
    for r in range(4, 9, 4):
        for s in range(1, 3):
            for p in range(1, 11):
                url = base_url.format(scale=s, rounds=r, page_num=p)
                yield url


def extract_url(url, proxies=None):
    r = session.get(url=url, headers=headers, cookies=cookies, proxies=proxies).text
    selector = html.fromstring(r)
    href_list = []
    for _ in selector.xpath('//div[@class="job-list"]/ul/li'):
        href = _.xpath('div/div[1]/h3/a/@href')
        if href:
            url = 'https://www.zhipin.com{}'.format(href[0])
            href_list.append({'url': url})
    return href_list


def main_extract():
    p = proxy()
    # while True:
    try:
        for _ in generate_url():
            print(_)
            urls = extract_url(url=_, proxies=p)
            if urls:
                print(urls)
                collection_url.insert_many(urls)
            time.sleep(.5)
    except Exception as e:
        print(e)
        # p = proxy()
        # continue
        time.sleep(2)


if __name__ == '__main__':
    main_extract()
    # print(read_mongodb())
    # for _ in generate_url():
    #     print(_)
    pass