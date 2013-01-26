'''
Created on Dec 21, 2012

@author: chupy
'''

import re
import timeit

def testperf():
    pattern = base + re.escape('HR/User/') + '[0-9\\-]+' + re.escape('/Resource/') + '([0-9\\-]+)'
    for k in range(100):
        re.match(pattern, 'http://localhost:8080/resources/HR/User/1/Resource/%s' % k)

if __name__ == '__main__':
    base = re.escape('http://localhost:8080/resources/')
    
    pattern = base + re.escape('HR/User/') + '([0-9\\-]+)' + re.escape('/Resource/') + '([0-9\\-]+)'
    print(pattern)
    print(re.match(pattern, 'http://localhost:8080/resources/HR/User/1/Resource/2').groups())
    
    print(timeit.timeit(testperf, number=100))
