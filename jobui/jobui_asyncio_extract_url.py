# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import pymongo
import json
import time
from lxml import html

url = 'http://www.jobui.com/process/'
data = {'nowPage': 65, 'secondCategory': '扑克棋牌', 'formAction': 'company_more_getRelateProduct'}
collection = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']['jobui_puke_url']
sema = asyncio.Semaphore(2)


async def fetch_content(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as res:
            text = await res.text()
            await asyncio.sleep(.5)
        return json.loads(text)['html']


async def extract_urls(url, data):
    with (await sema):
        selector = html.fromstring(await fetch_content(url, data))
        await asyncio.sleep(.3)
        href_list = []
        for _ in selector.xpath('//li[@class="products-logo products-bb"]'):
            href = _.xpath('div/p[1]/a/@href')
            product = _.xpath('div/p[1]/a/text()')
            if href:
                link = 'http://www.jobui.com{}'.format(href[0])
                href_list.append({'url': link, 'product': product[0]})
        # return href_list
        # collection.insert_many(href_list)
        print(href_list)


def main():
    t0 = time.time()
    data2 = [{'nowPage': _, 'secondCategory': '影音播放', 'formAction': 'company_more_getRelateProduct'} for _ in
             range(1, 65)]
    tasks = [extract_urls(url, d) for d in data2]
    # tasks = [extract_urls(url, data)]
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
