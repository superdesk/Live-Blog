'''
Created on Nov 25, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the omni module.
'''

import logging
logging.basicConfig(level=logging.DEBUG)

import unittest
from ally import omni

# --------------------------------------------------------------------

@omni.source('parent', 'children')
class A:

    def __init__(self):
        self.children = []
        self.parent = None
    
    @omni.resolver
    def action1(self):
        print('---------ACTION1')
        self.action2()

@omni.source('parent')  
class B:

    def __init__(self):
        self.parent = None
    
    @omni.resolver
    def action2(self):
        print('---------ACTION2')
        self.action2()
    
    @omni.resolver
    def main(self):
        self.action1()

class C:

    @omni.resolver
    def action2(self):
        print('---------LISTENER ACTION2:', omni.origin())
        #self.action2()
      
# --------------------------------------------------------------------

class TestOmni(unittest.TestCase):

    def testSucces(self):
        a = A()
        b = B()
        c = C()
        a.parent = b
        b.parent = a
        a.children.append(c)
        print(b.main())
        #self.assertTrue(b.start(omniClosest=True) == 'Heloo')
        

    # ----------------------------------------------------------------
    
    def testFailed(self):
        pass
        
# --------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
