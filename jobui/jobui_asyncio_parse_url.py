# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import pymongo
import time
from lxml import html

db = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']
collection = db['jobui_puke_app']
collection_url = db['jobui_puke_url']
# collection_filter_url = db['jobui_financing_filter_url']
collection_test = db['jobui_test2']
sema = asyncio.Semaphore(2)


def read_mongodb():
    urls = [_['url'] for _ in collection_url.find({})]
    return urls


async def parse_app(url):
    async with aiohttp.ClientSession() as session:
        with (await sema):
            async with session.get(url) as res:
                selector = html.fromstring(await res.text())
                await asyncio.sleep(.5)
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
                    app['url'] = url
                for i, _ in enumerate(selector.xpath('//ul[@class="j-download-origin company-product-download-origin"]/li'), 1):
                    download_rankings_amount = _.xpath('a/text()|span/text()')
                    app['download_rankings_amount_{}'.format(i)] = ','.join(str(i).strip() for i in download_rankings_amount)
                print(app)
                collection.insert(app)
                return app

def main():
    t0 = time.time()
    tasks = [parse_app(url) for url in read_mongodb()]
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*tasks))
    # print(results)
    # collection.insert_many(results)
    # for _ in results:
    #     print(_)
    #     collection.insert_many(_)
    loop.close()
    print(time.time() - t0)

if __name__ == '__main__':
    main()
    # print(read_mongodb().__len__())
