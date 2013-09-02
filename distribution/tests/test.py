'''
Created on Dec 21, 2012

@author: chupy
'''

from operator import attrgetter


if __name__ == '__main__':
    getter = attrgetter('endswith.aa')
    print(getter(''))