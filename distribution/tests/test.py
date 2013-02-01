'''
Created on Dec 21, 2012

@author: chupy
'''

import re
from urllib.parse import urlsplit, urlunsplit, urlencode


if __name__ == '__main__':
    base = re.compile('^resources(?:/|(?=\\.)|$)(.*)')
    m = base.match('resources/LiveDesk/Blog/1/Admin/')
    print(m.groups())
    m = base.match('resources')
    print(m.groups())
    print(re.sub('[\\/]+', '/', re.sub('([^\w\\/]*)', '', '^resources(?://|(?=\\.)|$)(.*)')))
    print(urlsplit('//localhost:8080/resources/?asa=as'))
    print(urlunsplit(('http', 'localhost:8080', '/resources/', urlencode((('name', 'value'))), '')))
