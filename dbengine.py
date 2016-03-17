# -*-coding:utf-8-*-
# Author: Shen Shen
# Email: dslwz2002@163.com

import datetime
import time
import pymongo
from pymongo import MongoClient
import numpy as np
import pandas as pd
from bson.code import Code
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

DBADRESS='127.0.0.1'
DBPORT=27017

def zhll_query(_year, _month, _day, _sbbh):
    client = MongoClient(DBADRESS, DBPORT)
    year = _year
    mon = _month
    day = _day
    SBBH = _sbbh
    db = client['trafficn']
    xqcoll = db['DY50_SP_SSSJ_LS']
    arr = []
    dt1 = datetime.datetime(year, mon, day, 0, 0, 0)
    dt2 = datetime.datetime(year, mon, day, 23, 59, 59)
    for item1 in xqcoll.find({'JSSJ': {'$lt': dt2, '$gte': dt1}, 'SBBH': SBBH}).sort('JSSJ'):
        dict = {'JSSJ': item1['JSSJ'].isoformat(' '), 'ZHLL': item1['ZHLL']}
        arr.append(dict)
    return arr

def distinct_cphm(year, month, day):
    client = MongoClient(DBADRESS, DBPORT)
    db = client['trafficn']
    qdate = datetime.date(year,month,day)
    colName = 'T_TGIS_VEHICLE_GPS_HIS_GPS_HIS%s' % (qdate.strftime('%Y%m%d'))
    taxiCol = db[colName]
    result = []
    idx = 1
    for item in taxiCol.distinct('CPHM'):
        obj = {}
        obj['id'] = idx
        obj['chepai'] = item.encode('utf-8')
        result.append(obj)
        idx += 1
    return result


def taxi_query(year, month, day, cphm, style):
    client = MongoClient(DBADRESS, DBPORT)
    db = client['trafficn']
    qdate = datetime.date(year,month,day)
    colName = 'T_TGIS_VEHICLE_GPS_HIS_GPS_HIS%s' % (qdate.strftime('%Y%m%d'))
    taxiCol = db[colName]
    result = []
    cur = taxiCol.find({'CPHM':cphm},{'_id':False,'JD':True,'WD':True,'GPS_TIME':True}).sort('GPS_TIME')
    if style:
        for doc in cur:
            obj={}
            obj['Lon'] = doc['JD']
            obj['Lat'] = doc['WD']
            dt = datetime.datetime.strptime(doc['GPS_TIME'],'%Y/%m/%d %H:%M:%S')
            obj['Time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
            result.append(obj)
    else:
        for doc in cur:
            dt = datetime.datetime.strptime(doc['GPS_TIME'],'%Y/%m/%d %H:%M:%S')
            jwd = [doc['JD'],doc['WD'],dt.strftime('%Y-%m-%d %H:%M:%S')]
            result.append(jwd)
    return result

def taxi_all_query(year, month, day, start, end):
    client = MongoClient(DBADRESS, DBPORT)
    db = client['trafficn']
    qdate = datetime.date(year,month,day)
    colName = 'T_TGIS_VEHICLE_GPS_HIS_GPS_HIS%s' % (qdate.strftime('%Y%m%d'))
    taxiCol = db[colName]

    dtStart = datetime.datetime(year, month, day, start, 0, 0)
    #[start,end)
    dtEnd = datetime.datetime(year, month, day, end-1, 59, 59)

    start = time.time()
    cur = taxiCol.find({'GPS_TIME':{'$gte':dtStart.strftime('%Y/%m/%d %H:%M:%S'),
                                '$lt':dtEnd.strftime('%Y/%m/%d %H:%M:%S')}})
    # print cur.count()
    taxiDict = {}
    for item in cur:
        if item['CPHM'] not in taxiDict:
            taxiDict[item['CPHM']]=[]
        taxiDict[item['CPHM']].append([item['JD'],item['WD']])
    end = time.time()
    print('consuming %s seconds' % (end-start))
    # print taxiDict
    result =[]
    idx = 1
    for k,v in taxiDict.items():
        # print k,v
        taxi = {}
        taxi['id'] = idx
        taxi['xylist'] = v
        result.append(taxi)
        idx += 1
    return result

def taxi_all_query_new(year, month, day, start, end):
    client = MongoClient(DBADRESS, DBPORT)
    db = client['trafficn']
    qdate = datetime.date(year,month,day)
    colName = 'T_TGIS_VEHICLE_GPS_HIS_GPS_HIS%s' % (qdate.strftime('%Y%m%d'))
    taxiCol = db[colName]

    dtStart = datetime.datetime(year, month, day, start, 0, 0)
    #[start,end)
    dtEnd = datetime.datetime(year, month, day, end-1, 59, 59)

    strStart = dtStart.strftime('%Y/%m/%d %H:%M:%S')
    strEnd = dtEnd.strftime('%Y/%m/%d %H:%M:%S')
    ###################
    mapper = Code("""
        function() {
            emit(this.CPHM, {data:[[this.JD,this.WD]]});
        };
    """)
    reducer = Code("""
        function(key, values) {
	        var ret = {data:[]}
            for(var i =0; i < values.length; i++){
                ret.data.push(values[i].data[0]);
            }
            return ret;
        };
    """)
    start = time.time()
    gpsresults = taxiCol.map_reduce(mapper, reducer, "gpsresults",
                                  query={"GPS_TIME":{"$gte":strStart,"$lt":strEnd}},
                                  sort={"GPS_TIME":1})
    end = time.time()
    print('consuming %s seconds'%(end-start))
    result = []
    for doc in gpsresults.find():
        taxi={}
        taxi['id']=doc['_id']
        taxi['xylist']=doc['value']['data']
        result.append(taxi)
    return result

def dgxq_locs():
    client = MongoClient(DBADRESS, DBPORT)
    db = client['trafficn']
    colName = 'DGXQ'
    taxiCol = db[colName]
    result = []
    for item in taxiCol.find({},{'_id':0,'SBDM':1,'SBMC':1,'JD':1,'WD':1,'JD84':1,'WD84':1})\
            .sort('QSSJ', pymongo.ASCENDING):
        result.append(item)
    return result


# return pd.DataFrame object
def dgxq_all():
    client = MongoClient(DBADRESS, DBPORT)
    db = client['trafficn']
    colName = 'DGXQ'
    taxiCol = db[colName]
    cursor = taxiCol.find({},{'_id':0,'SBDM':1,'SBMC':1})\
            .sort('SBDM', pymongo.ASCENDING)
    df = pd.DataFrame(list(cursor))
    return df


def dgxq_data(year, month, day):
    client = MongoClient(DBADRESS, DBPORT)
    db = client['trafficn']
    colName = 'DY50_XQ_SSSJ_LS'
    dgxqCol = db[colName]

    dtStart = datetime.datetime(year, month, day, 0, 0, 0)
    #[start,end)
    dtEnd = datetime.datetime(year, month, day+1, 0, 0, 0)
    # QSSJ have been converted to datetime , not string in this collection
    cursor = dgxqCol.find({'QSSJ':{'$gte':dtStart, '$lt':dtEnd}},{'_id':0,'SBBH':1,'FX':1,'ZHLL':1,'QSSJ':1})
        #.sort('QSSJ', pymongo.ASCENDING)
    #print(cursor.count())
    df = pd.DataFrame(list(cursor))
    return df



if __name__ == '__main__':
    # taxi_all_query(2015,9,21,13,15)
    # taxi_all_query_new(2015,9,21,13,15)
    print(dgxq_data(2015,7,21))
