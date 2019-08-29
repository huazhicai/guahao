"""
提取本地114gh数据，存入到服务器10.20.31.14 mongodb 的 kidney数据库中
"""
import pymongo

from config import MONGO_URL, MONGO_DB, MONGO_PORT


class Transfer(object):
    def __init__(self):
        self.local_client = pymongo.MongoClient(MONGO_URL, MONGO_PORT)
        self.local_db = self.local_client[MONGO_DB]
        self.local_col = self.local_db['guahao_info']

        self.remote_client = pymongo.MongoClient('10.20.31.14')
        self.remote_db = self.remote_client[MONGO_DB]
        self.remote_col = self.local_db['guahao_info']

    def transfer_data(self):
        for item in self.local_col.find():
            self.remote_col.update_one({'name': item['name'], 'link': item['link']}, {"$set": dict(item)}, upsert=True)
            print(item)


if __name__ == '__main__':
    obj = Transfer()
    obj.transfer_data()
