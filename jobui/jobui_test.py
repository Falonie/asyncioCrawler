import requests
from lxml import html
from multiprocessing import Pool
from concurrent import futures
from pprint import pprint
import pymongo
url = 'http://www.jobui.com/process/'
collection = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']['jobui']
session = requests.session()

def parse_url(url):
    data = {'nowPage': 301, 'secondCategory': '考试学习', 'formAction': 'company_more_getRelateProduct'}
    session = requests.session()
    r = session.post(url=url, data=data).json()
    selector = html.fromstring(r['html'])
    href_list = []
    for _ in selector.xpath('//li[@class="products-logo products-bb"]'):
        # href = _.xpath('a/@href')
        href=_.xpath('div/p[1]/a/@href')
        product=_.xpath('div/p[1]/a/text()')
        if href:
            link='http://www.jobui.com{}'.format(href[0])
            href_list.append({'link':link,'product':product[0]})
    return href_list


def parse_app(url):
    r = session.get(url).text
    selector = html.fromstring(r)
    app = {}
    for _ in selector.xpath('//div[@class="company-product-banner-desc"]'):
        product_name = _.xpath('span/text()')
        app['product_name'] = ''.join(str(i).strip() for i in product_name)
        company = _.xpath('div[1]/a/text()')
        app['company'] = ''.join(str(i).strip() for i in company)
        slogan = _.xpath('p[1]/text()')
        app['slogan'] = ''.join(str(i).strip() for i in slogan)
        download_amount = _.xpath('div[2]/div/span/text()')
        app['download_amount'] = ''.join(str(i).strip() for i in download_amount)
        update_time = _.xpath('p[2]/text()')
        app['update_time'] = ''.join(str(i).strip() for i in update_time)
    for i, _ in enumerate(selector.xpath('//ul[@class="j-download-origin company-product-download-origin"]/li'), 1):
        download_rankings_amount = _.xpath('a/text()|span/text()')
        app['download_rankings_amount_{}'.format(i)] = ''.join(str(i).strip() for i in download_rankings_amount)
    return app


def main_pool():
    with Pool() as pool:
        p = pool.map(parse_app, parse_url(url))
        # print(p)
    return p


# print(main_pool())

def main_threadpool():
    with futures.ThreadPoolExecutor() as executor:
        res = executor.map(parse_app, parse_url(url))
    return list(res)

if __name__ == '__main__':
    # r=main_threadpool()
    # print(r)
    # collection.insert_many(r)
    print(parse_url(url))