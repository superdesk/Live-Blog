'''
Created on Jun 12, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the util module.
'''

import unittest
from ally.util import Singletone, Uninstantiable

# --------------------------------------------------------------------

class Single(Singletone):
    '''
    '''

class CannotCreate(Uninstantiable):
    '''
    '''
    
# --------------------------------------------------------------------

class TestUtil(unittest.TestCase):

    def testSucces(self):
        s1 = Singletone()
        s2 = Singletone()
        
        self.assertTrue(s1 == s2)

    # ----------------------------------------------------------------
    
    def testFailed(self):
        s1 = Singletone()
        s2 = Singletone()
        
        self.assertFalse(s1 != s2)
        
        self.assertRaises(AssertionError, CannotCreate)
        
# --------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
