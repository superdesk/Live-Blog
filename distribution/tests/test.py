'''
Created on Dec 21, 2012

@author: chupy
'''

from urllib.parse import urlencode, urlunsplit

if __name__ == '__main__':
    print(urlencode({'spam': 1, 'eggs': 2, 'bacon': 0}))
    print(urlunsplit(('', '', 'asasas', None, '')))
    print('\xF0\x9F\x92\x8B')
    print('aa %(meta)s'.format(meta='\xF0\x9F\x92\x8B'))