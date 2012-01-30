'''
Created on Jun 9, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the API types module.
'''

from ally.api.type import Number, Integer, String, typeFor, Type, \
    Boolean
from ally import type_legacy as numbers
import unittest

# --------------------------------------------------------------------

class TestType(unittest.TestCase):
    
    def testSuccesBoolean(self):
        bt = typeFor(Boolean)

        self.assertTrue(isinstance(bt, Type))
        self.assertTrue(bt.forClass == bool)
        self.assertTrue(bt.isValid(True))
        
        bt = typeFor(bool)
        
        self.assertTrue(bt.isValid(False))
        self.assertTrue(bt.isValid(True))
        
    def testSuccesInt(self):
        it = typeFor(Integer)

        self.assertTrue(isinstance(it, Type))
        self.assertTrue(it.forClass == int)
        self.assertTrue(it.isValid(100))
        
        it = typeFor(int)
        
        self.assertTrue(it.isValid(-12))
        self.assertTrue(it.isValid(0))

    def testSuccesNumber(self):
        nt = typeFor(Number)

        self.assertTrue(isinstance(nt, Type))
        self.assertTrue(nt.forClass is numbers.Number)
        self.assertTrue(nt.isValid(100))
        
        nt = typeFor(float)
        
        self.assertTrue(nt.isValid(100.12))
        
        nt = typeFor(numbers.Number)
        
        self.assertTrue(nt.isValid(-1.12))
         
    def testSuccesStr(self):
        st = typeFor(String)

        self.assertTrue(isinstance(st, Type))
        self.assertTrue(st.forClass == str)
        self.assertTrue(st.isValid('ugu'))
        
        st = typeFor(str)
        
        self.assertTrue(st.isValid("heloo world"))
        self.assertTrue(st.isValid('Moi'))
        
    # ----------------------------------------------------------------
    
    def testFailedAsType(self):
        self.assertFalse(typeFor(TestType) != None)
    
    def testFailedBoolean(self):
        bt = typeFor(Boolean)

        self.assertFalse(bt.isValid(100.12))
        self.assertFalse(bt.isValid('heloo'))
        
    def testFailedInt(self):
        it = typeFor(Integer)
        
        self.assertFalse(it.isValid(100.12))
        self.assertFalse(it.isValid('heloo'))
        self.assertFalse(it.isValid(self))
    
    def testFailedNumber(self):
        nt = typeFor(Number)
        
        self.assertFalse(nt.isValid('as'))
        self.assertFalse(nt.isValid(self))
       
    def testFailedStr(self):
        st = typeFor(String)
        
        self.assertFalse(st.isValid(1))
        self.assertFalse(st.isValid(1.2))
        self.assertFalse(st.isValid(self))
        
# --------------------------------------------------------------------
  
if __name__ == '__main__':
    unittest.main()
