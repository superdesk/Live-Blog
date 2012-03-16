'''
Created on Jan 26, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the encoder and decoder xml.
'''

import unittest
from ally.support.core.util_param import parseStr
from urllib.parse import quote as encode

# --------------------------------------------------------------------

class TestDecoderUrlencoded(unittest.TestCase):
        
    def testSimple(self):
        urlQuery = 'simple=demo'
        self.assertDictEqual(parseStr(urlQuery), {'simple': 'demo'}, 'Simple: {0}'.format(urlQuery))

    def testSimpleMore(self):
        urlQuery = 'simple=demo&another=demo&last=is'
        self.assertDictEqual(parseStr(urlQuery), {'simple': 'demo', 'another': 'demo', 'last': 'is'}, 'Simple more params: {0}'.format(urlQuery))
        
    def testSimpleList(self):
        urlQuery = 'list[]=demo&list[]=demo&list[]=abc'
        parseDict = parseStr(urlQuery)
        self.assertDictEqual(parseDict, {'list': ['demo', 'demo', 'abc']}, 'Simple list: {0}'.format(urlQuery))
        
    def testDictList(self):
        urlQuery = 'list[demo][]=abc&list[demo][]=def&list[demo][]=xyz'
        parseDict = parseStr(urlQuery)
        self.assertDictEqual(parseDict, {'list': {'demo': ['abc', 'def', 'xyz']}}, 'Dict and list: {0}'.format(urlQuery))
        
    def testComplex(self):
        urlQuery = ('item1={0}&item2[key1.1][][subkey1.1][]={1}&item2[key1.1][][]={1}'
            '&item2[key2.1]={2}&item2[key3.1][subkey3.1]={3}&item3[key1.1][subkey1.1]={4}&noValue'
            ).format(encode('''!D"e#m$o%'''), 
                     encode('''&D'e(m)o*'''), 
                     encode('''+D e,m-o.'''), 
                     encode('''/D[e]m>o<'''), 
                     encode('Demo'))
        parseDict = parseStr(urlQuery)
        matchDict = { 
            'item1': '!D"e#m$o%',
            'item2': { 
                'key1.1': [{'subkey1.1': ["&D'e(m)o*"]}, "&D'e(m)o*"],
                'key2.1': '+D e,m-o.',
                'key3.1': {'subkey3.1': '/D[e]m>o<'}
            }, 
            'item3': {
                'key1.1': {'subkey1.1': 'Demo'} 
            },
            'noValue': None
        }
        self.assertDictEqual(parseDict, matchDict, 'Complex: {0}'.format(urlQuery)) 
                             


# --------------------------------------------------------------------
  
if __name__ == '__main__':
    unittest.main()
