'''
Created on Jun 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the API types module.
'''

import unittest
from ally.omni import Omni, doOmni

# --------------------------------------------------------------------

class Handler1:
    
    def do(self, event, *args, out):
        assert isinstance(event, Omni)
        event.exclude(self)
        out('Me First')
    
    def doPrint(self, event, message, out):
        assert isinstance(event, Omni)
        out(message)

# --------------------------------------------------------------------

class TestOmni(unittest.TestCase):
    
    def testSucces(self):
        values = []
        h1 = Handler1()
        
        doOmni(Omni('Print').add(h1).args('Hello', out=values.append))
        self.assertTrue(values == ['Me First', 'Hello'])
    
    # ----------------------------------------------------------------
    
    def testFailed(self):
        pass
        
# --------------------------------------------------------------------
  
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
