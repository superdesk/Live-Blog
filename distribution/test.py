'''
Created on Dec 20, 2011

@author: chupy
'''
import re

if __name__ == '__main__':
    m = re.compile('[a-z_\\.A-Z0-9]*\\_+[a-zA-Z0-9\\$]*$')
    print(dir(m))