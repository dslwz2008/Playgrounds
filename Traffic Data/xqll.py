# -*-coding:utf-8-*-
# Author: Shen Shen
# Email: dslwz2002@163.com
__author__ = 'Shen Shen'

from singleton import singleton

@singleton
class XqllBuffer(object):
    def __init__(self):
        self.max = 0
        self.min = 0
        self.steps = 0
        self.data = None
        self.dgxqCol = None


if __name__ == '__main__':
    b1 = XqllBuffer()
    b1.max = 10
    b1.min = 1

    b2 = XqllBuffer()
    print('max:{0}\tmin:{1}\n'.format(b2.max, b2.min))

    b2.max = 1000
    b2.min = 0
    print('max:{0}\tmin:{1}\n'.format(b1.max, b1.min))
