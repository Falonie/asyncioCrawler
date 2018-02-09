# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import pymongo
import json
import time
from lxml import html

url = 'http://www.jobui.com/process/'
data = {'nowPage': 333, 'secondCategory': '通讯社交', 'formAction': 'company_more_getRelateProduct'}
sema = asyncio.Semaphore(1)
collection = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']['jobui_url']


async def extract_urls_old(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as res:
            text = await res.text()
            # print(json.loads(text))
            selector = html.fromstring(json.loads(text)['html'])
            await asyncio.sleep(1)
            href_list = []
            for _ in selector.xpath('//li[@class="products-logo products-bb"]'):
                href = _.xpath('div/p[1]/a/@href')
                product = _.xpath('div/p[1]/a/text()')
                if href:
                    link = 'http://www.jobui.com{}'.format(href[0])
                    href_list.append({'url': link, 'product': product[0]})
            return href_list
            # print(href_list)


def main():
    t0 = time.time()
    data2 = [{'nowPage': _, 'secondCategory': '通讯社交', 'formAction': 'company_more_getRelateProduct'} for _ in
             range(101, 333)]
    # tasks = [extract_urls_old(url, data)]
    tasks = [extract_urls_old(url, d) for d in data2]
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*tasks))
    # print(results)
    # for _ in results:
    #     print(_)
    #     collection.insert_many(_)
    loop.close()
    print(time.time() - t0)


if __name__ == '__main__':
    main()
    # data2 = [{'nowPage': _, 'secondCategory': '通讯社交', 'formAction': 'company_more_getRelateProduct'} for _ in
    #          range(2, 100)]
    # print(data2)