'''
Created on Dec 21, 2012

@author: chupy
'''

import timeit
from http.client import HTTPConnection

# --------------------------------------------------------------------

REQUEST = b'GET /resources/Admin/Component/?X-Filter=Component.* HTTP/1.1\r\nAccept-Charset: utf-8\r\nConnection: keep-alive\r\nAccept: json\r\n\r\n'

# --------------------------------------------------------------------

def process(connection, headers):
    assert isinstance(connection, HTTPConnection)
    connection.request('GET', '/resources/Admin/Component/?X-Filter=Component.*&Authorization=1', None, headers)
    rsp = connection.getresponse()
    rsp.read()

def doAll():
    headers = {'Accept': 'json', 'Connection': 'keep-alive'}
    connection = HTTPConnection('localhost', 8080)
    
    for k in range(10):
        process(connection, headers)
        
    connection.close()
    
def doAllC():
    headers = {'Accept': 'json'}
    connection = HTTPConnection('localhost', 8080)
    
    for k in range(10):
        connection = HTTPConnection('localhost', 8080)
        process(connection, headers)
        connection.close()
        
# --------------------------------------------------------------------

if __name__ == '__main__':
    print(timeit.timeit(doAll, number=1))
