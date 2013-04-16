'''
Created on Jun 13, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides testing for the parameters decoding.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally.design.processor.attribute import requires, defines, optional
from ally.design.processor.context import Context, create
from ally.design.processor.spec import Resolvers
import unittest

# --------------------------------------------------------------------

class A(Context):
    p1 = requires(str)
    p2 = defines(int)

class B(Context):
    p1 = defines(str)

class C(Context):
    p2 = defines(int)

class D(Context):
    p2 = defines(str)
    
class F(D):
    p3 = defines(str)
    
class E(F, D):
    p2 = optional(str)
    p3 = optional(str)

resolvers = Resolvers(contexts=dict(I=B))
resolvers.merge(dict(I=F))
ctx = create(resolvers)
I = ctx['I']

# --------------------------------------------------------------------

class TestDesign(unittest.TestCase):

    def testContext(self):
        i = I()
        self.assertIsInstance(i, Context)
        self.assertNotIsInstance(i, A)
        self.assertIsInstance(i, B)
        self.assertNotIsInstance(i, C)
        self.assertIsInstance(i, D)
        self.assertIsInstance(i, F)
        self.assertIsInstance(i, E)
        
        self.assertTrue(B.p1 in i)

        self.assertRaises(AssertionError, setattr, i, 'p1', 12)
        i.p1 = 'astr'
        self.assertEqual(i.p1, 'astr')
        
# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()

