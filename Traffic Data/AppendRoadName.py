# -*-coding:utf-8-*-
# Author: Shen Shen
# Email: dslwz2002@163.com
__author__ = 'Shen Shen'

import pymongo
from multiprocessing import Pool

def main():
    client = pymongo.MongoClient('127.0.0.1', 27017)
    db = client['trafficn']
    dgxqCol = db['DGXQ']
    dgxq = dict()
    for doc1 in dgxqCol.find():
        dgxq[str(doc1['SBDM'])] = doc1
    xqData = db['DY50_XQ_SSSJ_LS']
    idx = 1
    for doc2 in xqData.find():
        name = dgxq[str(doc2['SBBH'])]['SBMC']
        xqData.update_one({'_id':doc2['_id']},{'$set':{'SBMC':name}})
        if idx % 10000 == 0:
            print idx
        idx += 1
    print 'finish!'
    # def datamap(doc2):
    #     name = dgxq[str(doc2['SBBH'])]['SBMC']
    #     xqData.update_one({'_id':doc2['_id']},{'$set':{'SBMC':name}})
    #
    # pool = Pool(4)
    # pool.map(datamap, xqData.find())
    # pool.close()
    # pool.join()



if __name__ == '__main__':
    main()