# -*- coding:utf-8 -*-

import tornado.web
import tornado.ioloop
import tornado.options
import json
import numpy as np
import pandas as pd
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
        try:
            year = int(self.get_argument('year',2015))
            month = int(self.get_argument('month',9))
            day = int(self.get_argument('day',21))
            interval = float(self.get_argument('interval',1.0))
            # query DGXQ collection
            if XqllBuffer().dgxqCol is None:
                XqllBuffer().dgxqCol = dgxq_all()

        except Exception, ex:
            print('{0}'.format(ex.message))
        finally:
            pass




class DgxqGetDataHandler(BaseHandler):
    def get(self):
        pass


application = tornado.web.Application([
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
