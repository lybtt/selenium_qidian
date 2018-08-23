# coding:utf-8
# author: 'lyb'
# Date:2018/8/23 15:25
import pymongo

from selenium_qidian.config import *


class UseMongo(object):
    """调用MongoDB数据库"""
    def __init__(self):
        client = pymongo.MongoClient(MONGO_URI)
        self.db = client[MONGO_DB]
        self.table = self.db[MONGO_TABLE]

    def save_to_mongo(self, book):
        """保存至数据库"""
        self.table.update({'title': book['title']}, {'$set': book}, True)
        print('存储成功 ：{}'.format(book['title']))

    def existed_url(self):
        """返回已经抓取到的数据列表"""
        # collections = db.collection_names()   输出所有的collection名字
        neir = self.db.get_collection(MONGO_TABLE)
        # 查询number字段,并将数据设置成集合
        existed_url_list = set()
        for x in neir.find({}, {"_id": 0, "number": 1}):
            existed_url_list.add(x['number'])
        return existed_url_list

    def check_field(self, fieldname):
        """返回存在某个字段的数据列表"""
        numbers = self.table.find({fieldname: {'$exists': False}}).count()
        print("有 {} 条数据 不存在指定的 '{}' 字段".format(numbers, fieldname))
        if numbers == 0:
            num_list = None
        # 因为url是后面才加入的，查询包含url字段的数据有多少条，
        else:
            num_list = [num['number'] for num in self.table.find({fieldname: {'$exists': True}})]
        # 查询不包含的数据
        return num_list


if __name__ == '__main__':
    # check_field('url')
    pass

