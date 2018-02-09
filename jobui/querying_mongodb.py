import pymongo,os
from pymongo import IndexModel, ASCENDING

db = pymongo.MongoClient(host='127.0.0.1', port=27017)['Falonie']
collection = db['jobui_puke_url']
collection_filter_duplicate=db['jobui_social_interaction_url_filter_duplicate']
for i, j in enumerate(collection.find({}), 1):
    print(i, j)
    pass

# index=IndexModel([('link',ASCENDING)],unique=True)
# collection.create_indexes([index])
# collection.drop()
# print(list(collection.list_indexes()))
# collection.drop_indexes()
# print([_ for _ in list(collection.find({}))])
# for _ in list(collection.find({})):
#     print(_['company'])
url_filter_duplicate={_['url'] for _ in collection.find({})}
print(url_filter_duplicate.__len__())
url_filter_duplicate_dict=[{'url':_} for _ in url_filter_duplicate]
# print(url_filter_duplicate_dict)
# collection_filter_duplicate.insert_many(url_filter_duplicate_dict)
company_list = [_.setdefault('company', '') for _ in list(collection.find({}))]
company_list = [_ for _ in company_list if _ == '']
print(company_list.__len__())

print(os.getcwd())