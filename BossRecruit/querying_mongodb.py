import pymongo, os

db = pymongo.MongoClient(host='localhost', port=27017)['Falonie']
collection = db['boss_recruit_上海_jobs_supplement']
collection_url = db['boss_recruit_上海_supplement_urls']
collection_filter = db['boss_recruit_上海_supplement_urls2']
collection_filter_duplicates_url = db['boss_recruit_上海_filter']
for i, _ in enumerate(collection.find({}), 1):
    print(i, _)
    pass

# collection_url.drop()
urls = {_['url'] for _ in collection_url.find({})}
urls_crawled = [_.setdefault('url', '') for _ in list(collection.find({}))]
urls_crawled = {_ for _ in urls_crawled if len(_) > 0}
# urls_crawled_non_empty=[_ for _ in collection.find({})]
urls_uncrawled = urls - urls_crawled
urls_dict = [{'url': _} for _ in urls_uncrawled]
print(urls.__len__(), urls_crawled.__len__(), urls_uncrawled.__len__(), urls_dict.__len__())
# collection_filter.insert_many(urls_dict)
print(os.path.abspath('.'))
# filter_duplicates={_.get('url') for _ in collection_url.find({})}-{_.get('url') for _ in collection.find({})}
# filter_duplicates_dict=[{'url':_} for _ in filter_duplicates]
# print(filter_duplicates_dict)
# collection_filter_duplicates_url.insert_many(filter_duplicates_dict)
# print({_.get('url') for _ in collection.find({})}.__len__())