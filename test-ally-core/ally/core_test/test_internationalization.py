'''
Created on May 27, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the internationalization module.
'''

import unittest
from ally import internationalization

_ = internationalization.translator(__name__)
# --------------------------------------------------------------------

class TestInternationalization(unittest.TestCase):

    def testSuccesMessage(self):
        self.assertTrue(_('Hello world') == 'Hello world')
        self.assertTrue(_('Hello $1', 'Gabriel') == 'Hello Gabriel')
        self.assertTrue(_('Hello $2 from $1', 'europe', 'Gabriel') == 'Hello Gabriel from europe')
        self.assertTrue(_('Hello $1 from $2 you have $3 euro', 'Gabriel', 'europe', 1000)\
                         == 'Hello Gabriel from europe you have 1000 euro')

    # ----------------------------------------------------------------
    
    def testFailedMessage(self):
        self.assertRaises(AssertionError, _, 'Hello $1')
        self.assertRaises(AssertionError, _, 'Hello $name', 'Gabriel')
        self.assertRaises(AssertionError, _, 'Hello $1 and $2', 'Gabriel')
        
# --------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
