import asyncio
import aiohttp
import pymongo
import time
from lxml import html

base_url = 'https://www.zhipin.com/c101020100/s_302-h_101020100/?page={num}&ka=page-{num}'
url = 'https://www.zhipin.com/c101020100/s_301-h_101020100/?page=5&ka=page-5'
collection = pymongo.MongoClient(host='localhost', port=27017)['Falonie']['boss_recruit_99']
sema = asyncio.Semaphore(5)


async def fetch_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            text = await res.text()
            await asyncio.sleep(4)
        return text


async def extract_url(url):
    with (await sema):
        selector = html.fromstring(await fetch_content(url))
        await asyncio.sleep(5)
        href_list = []
        for _ in selector.xpath('//div[@class="job-list"]/ul/li'):
            href = _.xpath('div/div[1]/h3/a/@href')
            if href:
                url = 'https://www.zhipin.com{}'.format(href[0])
                href_list.append({'url': url})
        collection.insert_many(href_list)
        print(href_list, href_list.__len__())


def main():
    t0 = time.time()
    # tasks = [extract_url(url)]
    urls = [base_url.format(num=_) for _ in range(1, 11)]
    tasks = [extract_url(url) for url in urls]
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()
    print(time.time() - t0)


if __name__ == '__main__':
    main()
    # print(urls)