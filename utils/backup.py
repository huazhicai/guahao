"""
提取本地114gh数据，备份到到Dell mongodb 的 kidney数据库中
"""
import pymongo

from config import *


class Backup(object):
    def __init__(self):
        self.local_client = pymongo.MongoClient(MONGO_URL, MONGO_PORT)
        self.local_db = self.local_client[MONGO_DB]
        self.local_coll = self.local_db['guahao_info']

        self.remote_client = pymongo.MongoClient(BACKUP_MONGO_URL)
        self.remote_db = self.remote_client[BACKUP_MONGO_DB]
        self.remote_coll = self.local_db['guahao_info']

    def backup_data(self):
        for item in self.local_coll.find():
            self.remote_coll.update_one({'name': item['name'], 'link': item['link']}, {"$set": dict(item)}, upsert=True)
            print(item)
        print('\n==========================================\n')


if __name__ == '__main__':
    obj = Backup()
    obj.backup_data()
