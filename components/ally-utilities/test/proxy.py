'''
Created on May 29, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the decorator module.
'''

import unittest
from ally.proxy import createProxy

# --------------------------------------------------------------------

class A:
    
    def methodA(self): pass
    
class B(A):
    
    def methodA(self): pass
    
    def methodB(self): pass

# --------------------------------------------------------------------

class TestProxy(unittest.TestCase):
        
    def testSuccesCreateProxy(self):
        proxy = createProxy(B)
        #TODO: continue
    
    # ----------------------------------------------------------------
        
    def testFailedCreateProxy(self):
        pass
        
# --------------------------------------------------------------------
  
if __name__ == '__main__':
    unittest.main()
