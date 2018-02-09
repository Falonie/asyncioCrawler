import asyncio
import aiohttp
import pymongo
import xlrd
import time
import re
from lxml import html

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
cookies = {
    'Cookie': '__c=1515999644; lastCity=101020100; JSESSIONID=""; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1515999646; __l=r=&l=%2F; toUrl=https%3A%2F%2Fwww.zhipin.com%2Fjob_detail%2F1416961389.html%3Fka%3Dsearch_list_1; __a=52065629.1515999644.1515999649.1515999644.34.3.32.34; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1516962048'}
url = 'https://www.zhipin.com/job_detail/1416985997.html?ka=search_list_1'
# file_path='/home/salesmind/python-date/FalonieRepository2/BossRecruit/boss_recruit_20_jobs_url.xlsx'
file_path = 'boss_recruit_闵行_未融资_99_url.xlsx'
db=pymongo.MongoClient(host='localhost', port=27017)['Falonie']
collection = db['boss_recruit_闵行_未融资_99_jobs']
collection_url=db['boss_recruit_闵行_未融资_99']
sema = asyncio.Semaphore(3)


def read_mongodb():
    urls = [_['url'] for _ in collection_url.find({})]
    return urls


def read_excel(file):
    with xlrd.open_workbook(file) as data_:
        table = data_.sheets()[0]
        url_list = [table.row_values(rownum)[0] for rownum in range(100, table.nrows)]
        # company_list_ = [table.row_values(rownum)[0] for rownum in range(0, 101)]
        return url_list


async def parse_url(url):
    async with aiohttp.ClientSession() as session:
        with (await sema):
            async with session.get(url) as res:
                selector = html.fromstring(await res.text())
                await asyncio.sleep(20)
                item = {}
                for _ in selector.xpath('//div[@class="job-primary detail-box"]/div[@class="info-primary"]'):
                    release_time = _.xpath('div[@class="job-author"]/span/text()')
                    item['release_time'] = ''.join(str(i) for i in release_time)
                    position = _.xpath('div[@class="name"]/text()')
                    item['position'] = ''.join(str(i) for i in position)
                for _ in selector.xpath('//div[@class="info-company"]'):
                    company = _.xpath('h3/a/text()')
                    item['company'] = ''.join(str(i) for i in company)
                    try:
                        item['rounds'], item['scale'], item['homepage'] = _.xpath('p/text()')
                    except Exception:
                        item['rounds'] = ','.join(str(i).strip() for i in _.xpath('p/text()'))
                    industry = _.xpath('p/a/text()')
                    item['industry'] = ''.join(str(i).strip() for i in industry)
                for _ in selector.xpath('//div[@class="job-detail"]'):
                    recruiter = _.xpath('div[@class="detail-op"]/h2/text()')
                    item['recruiter'] = ''.join(str(i) for i in recruiter)
                    recruiter_title = _.xpath('div[@class="detail-op"]/p/text()')
                    item['recruiter_title'] = ''.join(str(i) for i in recruiter_title)
                for _ in selector.xpath('//div[@class="job-detail"]/div[@class="detail-content"]'):
                    company_info = _.xpath('div[@class="job-sec company-info"]/descendant::text()')
                    item['company_info'] = ''.join(str(i).strip() for i in company_info)
                    job_description = _.xpath('div[1]/descendant::text()')
                    item['job_description'] = re.sub(r'[\t\s\n\xa0 ]','',''.join(str(i).strip() for i in job_description))
                    business_info_company = _.xpath('div[4]/div[@class="name"]/text()|div[2]/div[@class="name"]/text()')
                    item['business_info_company'] = ''.join(str(i).strip() for i in business_info_company)
                    work_location = _.xpath(
                        'div[5]/h3/text()|div/div[@class="job-location"]/div[@class="location-address"]/text()')
                    item['work_location'] = ''.join(str(i).strip() for i in work_location)
                    item['url'] = url
                print(item)
                collection.insert(item)


def main():
    t0 = time.time()
    # tasks = [parse_url(url) for url in read_mongodb()]
    tasks = [parse_url(url) for url in read_excel(file_path)]
    # tasks = [parse_url(url)]
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()
    print(time.time() - t0)


if __name__ == '__main__':
    main()
    # print(read_excel(file_path).__len__())
    # print(read_mongodb().__len__())