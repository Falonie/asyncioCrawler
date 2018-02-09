import requests, pymongo, time
from lxml import html
from multiprocessing import Pool
from concurrent import futures

url = 'http://www.jobui.com/company/12549419/products/43530/'
url2 = 'http://www.jobui.com/company/12549419/products/'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
cookies = {
    'Cookie': 'jobui_area=%25E4%25B8%258A%25E6%25B5%25B7; jobui_p=1516275390197_63429998; Hm_lvt_8b3e2b14eff57d444737b5e71d065e72=1516275390; jobui_seSun=1; jobui_user_passport=yk151627543486844; PHPSESSID=4gbaoia7ap0jh0bopikisnl2q3; jobui_user_searchURL=http%3A%2F%2Fm.jobui.com%2Fjobs%3FjobKw%3D%25E5%25B0%258F%25E8%2588%25B9%25E5%2587%25BA%25E6%25B5%25B7%25E6%2595%2599%25E8%2582%25B2%25E7%25A7%2591%25E6%258A%2580%25E6%259C%2589%25E9%2599%2590%25E5%2585%25AC%25E5%258F%25B8%26cityKw%3D%25E4%25B8%258A%25E6%25B5%25B7%26sortField%3Dlast; TN_VisitCookie=18; TN_VisitNum=4; Hm_lpvt_8b3e2b14eff57d444737b5e71d065e72=1516848081'}
session = requests.session()
collection = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']['jobui_app']
collection_url = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']['jobui_url']


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


# print(parse_app(url))
def parse_page(url):
    r = session.get(url).text
    selector = html.fromstring(r)
    urls = []
    for _ in selector.xpath('//div[@class="jk-box"]/ul/li'):
        href = _.xpath('div[2]/a/@href')
        if href:
            link = 'http://www.jobui.com{}'.format(href[0])
            # product=_.xpath('div[2]/a/text()')
            # print(link)
            urls.append(link)
    return urls


def read_mongodb():
    urls = [_['link'] for _ in collection_url.find({})]
    return urls


# print(parse_page(url2))
def main_pool():
    with Pool() as pool:
        # p = pool.map_async(parse_app, read_mongodb())
        p = pool.map(parse_app, parse_page(url2))
        print(p)
        # collection.insert_many(p)
    # return p


# print(main_pool())

def main_threadpool():
    with futures.ThreadPoolExecutor() as executor:
        res = executor.map(parse_app, parse_page(url2))
    return list(res)


if __name__ == '__main__':
    t0 = time.time()
    print(main_pool())
    # print(read_mongodb())
    # print(parse_page(url2))
    print(time.time() - t0)
    # print(main_threadpool())