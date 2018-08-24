# coding:utf-8
# author: 'lyb'
# Date:2018/8/23 20:13
import os
from collections import defaultdict

import xlwt

from db import *
from bson import SON

data = UseMongo()


def field_value_count(fieldname, num):
    """返回指定字段的前n位"""
    pipeline = [
        {"$unwind": "${}".format(fieldname)},
        {"$group": {"_id": "${}".format(fieldname), "count": {"$sum": 1}}},
        {"$sort": SON([("count", -1), ("_id", -1)])}
    ]
    result = list(data.table.aggregate(pipeline))[:num]
    print(result)
    # 导出 excel
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('top {} author'.format(num))
    field_list = ['_id', 'count']
    for i in range(num+1):
        if i == 0:
            for n in range(2):
                sheet.write(i, n, field_list[n])
        else:
            for n in range(2):
                sheet.write(i, n, result[i-1][field_list[n]])
    save_data_xls(wbk, 'top {} author.xls'.format(num))


def sort_score(fieldname, num):
    """查询前多少排名的评分的书籍"""
    result = data.table.find(
        projection={'_id': False, 'number': True, "score": True, 'author': True, 'title': True, 'tags': True, 'score_people': True, 'chapter': True})\
        .limit(num).sort([(fieldname, pymongo.DESCENDING)])     # DESCENDING 倒序   ASCENDING  升序
    clean_result = []
    for i in result:
        i['tags'] = i['tags'][0].strip('完本 VIP 签约 ').strip(' ').split(' ')
        clean_result.append(i)
    return clean_result


def count_tags(num):
    """查询标签的排序"""
    tags_dict = defaultdict(int)
    result = data.table.find({}, projection={'_id': 0, 'tags': 1})         # 找到所有的标签数据
    for i in result:
        one_tags_list = i['tags'][0].strip('完本 VIP 签约 ').strip(' ').split(' ')
        for i in one_tags_list:
            tags_dict[i] += 1
    tags_dict = sorted(tags_dict.items(), key=lambda x: x[1], reverse=True)   # 字典排序
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('top {} tags'.format(num))
    field_list = ['标签', '总数']
    for i in range(num + 1):
        if i == 0:
            for n in range(len(field_list)):
                sheet.write(i, n, field_list[n])
        else:
            try:
                for n in range(len(field_list)):
                    sheet.write(i, n, tags_dict[i-1][n])
            except IndexError:
                num = i - 1
                break
    save_data_xls(wbk, 'top {} tags.xls'.format(num))
    return tags_dict[:num]


def write_xls(num):
    """将数据保存成xls格式"""
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('top {}'.format(num))
    field_list = ['number', 'title', 'author', 'score', 'score_people', 'tags', 'chapter']
    for i in range(num):
        if i == 0:
            for n in range(7):
                sheet.write(i, n, field_list[n])
        else:
            result = data.table.find_one({'number': i})
            for n in range(7):
                if n == 5:
                    sheet.write(i, n, result[field_list[n]][0].strip('完本 VIP 签约 ').strip(' '))  # 标签去掉前三个都有的
                else:
                    sheet.write(i, n, result[field_list[n]])
    save_data_xls(wbk, 'top-{}.xls'.format(num))
    print('task is done')


def save_data_xls(wbk, title):
    try:
        wbk.save('data/' + title)
    except FileNotFoundError:
        os.mkdir('data')
        wbk.save('data/' + title)
    print(title + '以保存')


if __name__ == '__main__':
    # field_value_count('author', 10)
    # for i in sort_score('score', 10):
    #     print(i)
    print(count_tags(100))
    # write_xls(501)
    pass
