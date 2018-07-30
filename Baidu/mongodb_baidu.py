from pymongo import MongoClient


def mongo_connection(host="localhost", port=27017, username=None, password=None):
    if username and password:
        mongo_uri = f'mongodb://{username}:{password}@{host}:{port}'
        return MongoClient(mongo_uri)
    return MongoClient(f'mongodb://{host}:{port}')


collection = mongo_connection()['Falonie']['Baidu_Search2']
for i, j in enumerate(collection.find(), 1):
    print(i, j)

# collection.drop()
