# -*- coding:utf-8 -*-

import tornado.web
import tornado.ioloop
import tornado.options
import json
import numpy as np
import pandas as pd
import datetime
from xqll import XqllBuffer
from dbengine import *
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class BaseHandler(tornado.web.RequestHandler):
     def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')


class ZhllcxHandler(BaseHandler):
    def get(self):
        year = int(self.get_argument('year'))
        month = int(self.get_argument('month'))
        day = int(self.get_argument('day'))
        sbbh = self.get_argument('sbbh')
        result = zhll_query(year, month, day, sbbh)

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result))


class MainHandler(BaseHandler):
    def get(self, *args, **kwargs):
        result = {'status':'ok'}
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result))

class TaxicxHandler(BaseHandler):
    def get(self, *args, **kwargs):
        year = int(self.get_argument('year',2015))
        month = int(self.get_argument('month',7))
        day = int(self.get_argument('day',1))
        cphm = self.get_argument('cphm',u'浙FA1G82')
        result = taxi_query(year, month, day, cphm, 0)

        self.set_header('Content-Type', 'application/json;charset:utf-8')
        self.write(json.dumps(result))


class TaxiGPSCxHandler(BaseHandler):
    def get(self, *args, **kwargs):
        year = int(self.get_argument('year',2015))
        month = int(self.get_argument('month',7))
        day = int(self.get_argument('day',1))
        cphm = self.get_argument('cphm',u'浙FA1G82')
        result = taxi_query(year, month, day, cphm, 1)

        self.set_header('Content-Type', 'application/json;charset:utf-8')
        self.write(json.dumps(result))

class TaxiAllCxlHandler(BaseHandler):
    def get(self, *args, **kwargs):
        year = int(self.get_argument('year',2015))
        month = int(self.get_argument('month',7))
        day = int(self.get_argument('day',1))
        start = int(self.get_argument('start',7))
        end = int(self.get_argument('end',9))
        #result = taxi_all_query(year, month, day, start, end)
        result = taxi_all_query_new(year, month, day, start, end)

        self.set_header('Content-Type', 'application/json;charset:utf-8')
        self.write(json.dumps(result))


class GetCPHMHandler(BaseHandler):
    def get(self, *args, **kwargs):
        year = int(self.get_argument('year',2015))
        month = int(self.get_argument('month',7))
        day = int(self.get_argument('day',1))
        result = distinct_cphm(year,month,day)

        self.set_header('Content-Type', 'application/json;charset:utf-8')
        self.write(json.dumps(result))

class DgxqLocHandler(BaseHandler):
    def get(self):
        result = dgxq_locs()
        self.set_header('Content-Type', 'application/json;charset:utf-8')
        self.write(json.dumps(result))


class DgxqStatsHandler(BaseHandler):
    def get(self):
        result={}
        try:
            year = int(self.get_argument('year',2015))
            month = int(self.get_argument('month',9))
            day = int(self.get_argument('day',21))
            interval = int(self.get_argument('interval',60))
            #
            # # query DGXQ collection
            # if XqllBuffer().dgxqCol is None:
            #     XqllBuffer().dgxqCol = dgxq_all()
            dgxqDf = dgxq_data(year,month,day)

            # merge
            # merged = pd.merge(dgxqDf,XqllBuffer().dgxqCol,left_on='SBBH',right_on='SBDM')
            dgxqDf.set_index(pd.DatetimeIndex(dgxqDf['QSSJ']),inplace=True)

            # filter by time
            delta = datetime.timedelta(minutes=interval)
            dtStart = datetime.datetime(year, month, day, 0, 0, 0)
            #[start,end)
            dtEnd = datetime.datetime(year, month, day+1, 0, 0, 0)
            dtTemp = dtStart + delta
            steps = 1440/interval
            XqllBuffer().data = [None] * steps
            idx = 0
            minll = 10000 # a big number
            maxll = 0
            while dtTemp <= dtEnd:
                # There is a bug in this function. The last step returns empty list.
                # So I use the selector instead.
                # filtered = dgxqDf.between_time(start_time=dtStart, end_time=dtTemp,
                #                                include_start=True, include_end=False)
                selector = (dgxqDf['QSSJ']>=dtStart) & (dgxqDf['QSSJ']<dtEnd)
                filtered = dgxqDf[selector]
                grouped = filtered.groupby([filtered['SBMC'],filtered['SBBH'],filtered['FX']])
                objArray = []
                for (name,group) in grouped:
                    obj={}
                    #obj['id']='{0}_{1}_{2}'.format(name[0], name[1], name[2])
                    obj['id']='%s_%s_%s' % (name[0],name[1],name[2])
                    obj['zhll']=group['ZHLL'].mean()
                    if obj['zhll'] > maxll:
                        maxll = obj['zhll']
                    if obj['zhll'] < minll:
                        minll = obj['zhll']
                    objArray.append(obj)
                XqllBuffer().data[idx] = objArray
                dtStart = dtTemp
                dtTemp = dtStart + delta
                idx += 1

            # result data
            result['max']=maxll
            result['min']=minll
            result['steps']=steps
            result['success']=True

        except Exception, ex:
            print('ERROR: %s' % str(ex))
            result['success']=False
            result['message']='ERROR: %s' % str(ex)
        finally:
            self.set_header('Content-Type', 'application/json;charset:utf-8')
            self.write(json.dumps(result))


class DgxqGetDataHandler(BaseHandler):
    def get(self):
        result={}
        try:
            step = int(self.get_argument('step',1))
            data = XqllBuffer().data[step-1]
            result['success'] = True
            result['data'] = data
        except Exception, ex:
            print('ERROR: %s' % str(ex))
            result['success']=False
            result['message']='ERROR: %s' % str(ex)
        finally:
            self.set_header('Content-Type', 'application/json;charset:utf-8')
            self.write(json.dumps(result))


class DgxqZHLLAtTimeHandler(BaseHandler):
    def get(self, *args, **kwargs):
        result = {}
        try:
            # default is 2015.7.1(1438358400000)
            millisec = int(self.get_argument('time',1438358400000/1000))/1000
            dt = datetime.datetime.fromtimestamp(millisec)
            objArr = []
            docs, min, max = dgxq_zhll_at(dt)
            for doc in docs:
                obj={}
                obj['id']='%s_%s_%s' % (doc['SBMC'],doc['SBBH'],doc['FX'])
                obj['zhll']=doc['ZHLL']
                objArr.append(obj)
            result['success'] = True
            result['data'] = objArr
            result['min'] = min
            result['max'] = max
        except Exception, ex:
            print('ERROR: %s' % str(ex))
            result['success']=False
            result['message']='ERROR: %s' % str(ex)
        finally:
            self.set_header('Content-Type', 'application/json;charset:utf-8')
            self.write(json.dumps(result))

class DgxqZHLLBetweenTimeHandler(BaseHandler):
    def get(self, *args, **kwargs):
        result = {}
        try:
            # default is 2015.7.1 08:05:00 (1435709100000)
            # to 2015.7.1 08:10:00 (1435709400000)
            startms = int(self.get_argument('start',1435709100000/1000))/1000
            endms = int(self.get_argument('end',1435709400000/1000))/1000
            startDt = datetime.datetime.fromtimestamp(startms)
            endDt = datetime.datetime.fromtimestamp(endms)
            style = int(self.get_argument('style',0))
            datalist, min, max = dgxq_zhll_between(startDt, endDt)
            objArr = []
            # raw data
            if style == 0:
                for doc in datalist:
                    obj={}
                    obj['id']='%s_%s_%s' % (doc['SBMC'],doc['SBBH'],doc['FX'])
                    obj['zhll']=doc['ZHLL']
                    objArr.append(obj)
            else:
                df = pd.DataFrame(datalist)
                grouped = df.groupby([df['SBMC'],df['SBBH'],df['FX']])
                for (name,group) in grouped:
                    obj={}
                    obj['id']='%s_%s_%s' % (name[0],name[1],name[2])
                    obj['zhll']=group['ZHLL'].mean()
                    objArr.append(obj)
            result['success'] = True
            result['data'] = objArr
            result['min'] = min
            result['max'] = max
        except Exception, ex:
            print('ERROR: %s' % str(ex))
            result['success']=False
            result['message']='ERROR: %s' % str(ex)
        finally:
            self.set_header('Content-Type', 'application/json;charset:utf-8')
            self.write(json.dumps(result))


application = tornado.web.Application([
    (r"^/dgxq/zhllbetween$", DgxqZHLLBetweenTimeHandler),
    (r"^/dgxq/zhllat$", DgxqZHLLAtTimeHandler),
    (r"^/dgxq/stats$", DgxqStatsHandler),
    (r"^/dgxq/getdata$", DgxqGetDataHandler),
    (r"^/getcphm$", GetCPHMHandler),
    (r"^/taxigpscx$", TaxiGPSCxHandler),
    (r"^/taxicx$", TaxicxHandler),
    (r"^/taxiallcx$", TaxiAllCxlHandler),
    (r"^/zhllcx$", ZhllcxHandler),
    (r"^/getdgxq$", DgxqLocHandler),
    (r"^/$", MainHandler)
])

if __name__ == "__main__":
    application.listen(8080)
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.current().start()
