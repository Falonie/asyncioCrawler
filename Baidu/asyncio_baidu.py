import re
import time
import asyncio
import aiohttp
import logging
import pymongo
import xlrd
from lxml import html

file = 'Company_list.xlsx'


class Baidu(object):
    BASE_URL = 'http://www.baidu.com/s?q1={}@V'
    db = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']
    collection = db['Baidu_Search2']
    logging.basicConfig(filename='baidu.log', format='%(levelname)s:%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S: %p', level=logging.DEBUG)

    async def asynchronous_baidu_search(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=None) as response:
                # print(await response.text())
                company_name = re.findall('q1=(.*?)@V', url)[0]
                search_result = []
                selector = html.fromstring(await response.text())
                try:
                    result = {}
                    result['company_name'] = company_name
                    result['search_item'] = selector.xpath(
                        '//div[@class="ecl-vmp-card2"]/div[@class="ecl-vmp-contianer c-border"]/'
                        'div[@class="c-row section header-section"]/h2/text()')[0]
                    link = selector.xpath('//div[@class="c-row section main-section last"]/'
                                          'div[1]/table/tr[2]/td/a[1]/text()')[0]
                    result['link'] = re.sub('\xa0', '', link)
                    result['authentication'] = True
                    search_result.append(result)
                except Exception:
                    for i in selector.xpath('//div[@id="content_left"]/div[position()<7]'):
                        result = {}
                        result['company_name'] = company_name
                        result['search_item'] = ''.join(str(i).strip() for i in i.xpath('h3/a/descendant::text()'))
                        link = i.xpath('div/div[@class="c-span18 c-span-last"]/div[@class="f13"]/a/descendant::text()|'
                                       'div[@class="f13"]/a/text()|div/div[2]/p[2]/span[1]/text()')
                        link = [''.join(str(i).strip() for i in link).replace('百度快照', '')]
                        if not link:
                            link = ['']
                        result['link'] = re.sub('\xa0', '', link[0])
                        result['authentication'] = False
                        search_result.append(result)
                finally:
                    print(search_result)
                    try:
                        self.collection.insert_many(search_result)
                    except Exception as e:
                        print(e)

    def company_list(self, file):
        with xlrd.open_workbook(file) as data:
            table = data.sheets()[0]
            company_list_ = [table.row_values(rownum)[0] for rownum in range(1, table.nrows)]
            # company_list_ = [table.row_values(rownum)[0] for rownum in range(1, 10)]
            return company_list_

    def main(self):
        t0 = time.time()
        company_urls = [self.BASE_URL.format(i) for i in self.company_list(file=file)]
        tasks = [self.asynchronous_baidu_search(url) for url in company_urls]
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        print(time.time() - t0)
        logging.debug(time.time() - t0)


if __name__ == '__main__':
    baidu = Baidu()
    baidu.main()
