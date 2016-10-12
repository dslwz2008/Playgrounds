# -*-coding:utf-8-*-
# Author: Shen Shen
# Email: dslwz2002@163.com

import pymongo
import datetime
import unicodecsv
import calendar
client = pymongo.MongoClient('127.0.0.1', 27017)
db = client['trafficn']
dgxqCol = db['DY50_XQ_SSSJ_LS']
EXPORT_DIR='export'

def statByDay():
    startDt = datetime.datetime(2015,7,1)
    delDt = datetime.timedelta(days=1)
    endDt = startDt + delDt
    finishDt = datetime.datetime(2015,10,1)

    while endDt <= finishDt:
        pipeline=[
            {
                '$match':{
                    'QSSJ':{
                        '$gte':startDt,
                        '$lt':endDt
                    }
                }
            },
            {
                '$project':{'_id':0,'SBMC':1,'ZHLL':1}
            },
            {
                '$group':{
                    '_id':'$SBMC',
                    'total':{'$sum':'$ZHLL'}
                }
            }
        ]
        result = list(dgxqCol.aggregate(pipeline))
        filename = '%s/%s-%s-%s.csv'%(EXPORT_DIR,startDt.year,startDt.month,startDt.day)
        fieldnames = ['_id', 'total']
        with open(filename, 'w') as f:
            writer = unicodecsv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(result)
        print('finish %s'%filename)
        startDt = endDt
        endDt += delDt

def statByMonth():
    month = [7,8,9]
    days = [calendar.monthrange(2015, m)[1] for m in month]
    startDt = datetime.datetime(2015,7,1)
    idx = 0
    delDt = datetime.timedelta(days[idx])
    endDt = startDt + delDt
    finishDt = datetime.datetime(2015,10,1)

    while endDt <= finishDt:
        pipeline=[
            {
                '$match':{
                    'QSSJ':{
                        '$gte':startDt,
                        '$lt':endDt
                    }
                }
            },
            {
                '$project':{'_id':0,'SBMC':1,'ZHLL':1}
            },
            {
                '$group':{
                    '_id':'$SBMC',
                    'total':{'$sum':'$ZHLL'}
                }
            }
        ]
        result = dgxqCol.aggregate(pipeline)
        filename = '%s/%s-%s.csv'%(EXPORT_DIR,startDt.year,startDt.month)
        fieldnames = ['_id', 'total']
        with open(filename, 'w') as f:
            writer = unicodecsv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(result)
        print('finish %s'%filename)
        idx += 1
        if idx == len(days):
            break
        delDt = datetime.timedelta(days[idx])
        startDt = endDt
        endDt += delDt

if __name__ == '__main__':
    # statByDay()
    statByMonth()