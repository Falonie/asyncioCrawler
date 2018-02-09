import pymongo
import logging
import os
from pymongo import IndexModel, ASCENDING

# LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
db = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']
collection = db['jobui_puke_app']
collection_filter_empty_items=db['jobui_travel_app2']
collection_url = db['jobui_puke_url']
collection_filter_url = db['jobui_travel_url_supplyment2']
for i, j in enumerate(collection.find({}), 1):
    # print(i, j)
    pass
print('crawled item amount')
print(list(collection.find({})).__len__())
urls = [_['url'] for _ in collection_url.find({})].__len__()
urls_filter_duplicates=set([_['url'] for _ in collection_url.find({})])
print('total')
print(set([_['url'] for _ in collection_url.find({})]).__len__())
# all urls
print(urls)
print(urls_filter_duplicates.__len__())

company_list = [_.setdefault('company', '') for _ in list(collection.find({}))]
company_list = [_ for _ in company_list if _ == '']
print('empty items')
print(company_list.__len__())
url_list = [_.setdefault('url', '') for _ in list(collection.find({}))]
url_list = [_ for _ in url_list if len(_) > 0]
print('crawled item whose url is not empty')
print(url_list.__len__())
url_list_dict=[_ for _ in collection.find({}) if _.setdefault('url','')!='']
# collection_filter_empty_items.insert_many(url_list_dict)
# print(url_list_dict)
# print([_['link'] for _ in collection_url.find({})])
filter_url = [_['url'] for _ in collection_url.find({}) if _['url'] not in url_list]
# print([_ for _ in url_list].__len__())
print('uncrawled urls')
print(filter_url.__len__())
# transfer uncrawled urls to dict
# logging.debug('transfer uncrawled urls to dict')
filter_url_dict = [{'url': _} for _ in filter_url]
print(filter_url_dict.__len__())
# collection_filter_url.insert_many(filter_url_dict)

print(os.getcwd())