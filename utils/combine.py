"""
__author__ = seven
"""
import pymongo
from config import MONGO_URL, MONGO_PORT, MONGO_DB


class Combination(object):
    """
    合并集合 departments outpatient 信息 到集合guahao_info
    """

    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_URL, MONGO_PORT)
        self.db = self.client[MONGO_DB]
        self.departments = self.db['departments']  # 肾病科集合
        self.outpatient = self.db['outpatient']  # 门诊信息集合

        self.official = self.db['official']  # 提取ID，作为联结 union_id

        self.guahao = self.db['guahao_info']  # 存储集合

    def combine_data(self):
        doctors = set([name.get('doctorName') for name in self.outpatient.find({}, {'doctorName': 1})])
        for doctor in doctors:
            outpatient = [{'dutyDate': item['dutyDate'], 'totalFee': item.get('totalFee', None),
                           'remainAvailableNumber': item['remainAvailableNumber']} for item in
                          self.outpatient.find({'doctorName': doctor})]
            dict_1 = self.outpatient.find_one({'doctorName': doctor})
            dict_2 = self.departments.find_one({'link': {"$regex": dict_1['hospId']}})
            pattern_website = dict_2.get('website', None).split('.')[1] if dict_2.get('website', None) else ' '
            dict_3 = self.official.find_one({'name': dict_1['doctorName'][:3], 'link': {"$regex": pattern_website}})
            union_id = dict_3.get('_id') if dict_3 else None

            yield {
                'city': dict_2['city'],
                'hospital': dict_2['hospital'],
                'website': dict_2.get('website', None),
                'grade': dict_2['grade'],
                'department': dict_2['department'],
                'phone': dict_2['phone'],
                'link': dict_2['link'],
                'union_id': union_id,
                'name': dict_1['doctorName'],
                'title': dict_1['doctorTitleName'],
                'special': dict_1['skill'],
                'outpatient_info': outpatient
            }

    def save_to_mongo(self):
        for item in self.combine_data():
            self.guahao.update_one({'name': item['name'], 'link': item['link']}, {"$set": dict(item)}, upsert=True)
            print(item)
        print("\n========================================================\n")


if __name__ == '__main__':
    combine = Combination()
    combine.save_to_mongo()
