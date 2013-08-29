'''
Created on Dec 21, 2012

@author: chupy
'''

import hashlib
import binascii
import os
import re

if __name__ == '__main__':
    a = hashlib.md5()
    print(a.update(b'afdasdasdfqegfqegf'))
    print(a.update(121212))
    print(a.hexdigest().upper())