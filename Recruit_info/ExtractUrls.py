import asyncio
import aiohttp
import pymongo
import time
from lxml import html

collection = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']['app_urls']


async def extract_urls(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy=None) as response:
            sel = html.fromstring(await response.text())
            # urls = [_ for _ in sel.xpath('//div[@id="resultList"]/div[@class="el"]/p/span/a/@href')]
            urls = [{'url': _} for _ in sel.xpath('//div[@id="resultList"]/div[@class="el"]/p/span/a/@href')]
            try:
                collection.insert_many(urls)
            except Exception as e:
                print(e)
            print(urls)
            return urls


def main():
    t0 = time.time()
    url = 'http://search.51job.com/list/010000,000000,0000,00,9,99,app,2,{}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
    urls = [url.format(_) for _ in range(1, 17)]
    tasks = [extract_urls(url) for url in urls]
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*tasks))
    # try:
    #     collection.insert_many(results)
    # except Exception as e:
    #     print(e)
    # print(results, len(results))
    loop.close()
    print(time.time() - t0)


if __name__ == '__main__':
    main()
