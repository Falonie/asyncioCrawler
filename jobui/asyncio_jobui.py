import asyncio
import aiohttp
import pymongo
import json
import time
from lxml import html

url = 'http://www.jobui.com/process/'
data = {'nowPage': 65, 'secondCategory': '扑克棋牌', 'formAction': 'company_more_getRelateProduct'}
collection = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']['jobui_puke_url']
sema = asyncio.Semaphore(1)


async def fetch_content(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as res:
            text = await res.text()
            await asyncio.sleep(.5)
        return json.loads(text)['html']


async def parse_app(url):
    async with aiohttp.ClientSession() as session:
        # with (await sema):
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
            for i, _ in enumerate(selector.xpath('//ul[@class="j-download-origin company-product-download-origin"]/li'),
                                  1):
                download_rankings_amount = _.xpath('a/text()|span/text()')
                app['download_rankings_amount_{}'.format(i)] = ','.join(
                    str(i).strip() for i in download_rankings_amount)
            # print(app)
            # collection.insert(app)
            return app


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
                # href_list.append({'url': link, 'product': product[0]})
                href_list.append(link)
        tasks = [parse_app(u) for u in href_list]
        content = await asyncio.gather(*tasks)
        # print(content)
        for c in content:
            print(c)


if __name__ == '__main__':
    t0 = time.time()
    data2 = [{'nowPage': _, 'secondCategory': '影音播放', 'formAction': 'company_more_getRelateProduct'} for _ in
             range(1, 4)]
    tasks = [extract_urls(url, d) for d in data2]
    loop = asyncio.get_event_loop()
    loop.close()
    print(time.time() - t0)