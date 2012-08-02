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

from ally.design.context import Context, requires, defines, optional
import unittest

# --------------------------------------------------------------------

class A(Context):
    p1 = requires(str)
    p2 = defines(int)

class B(Context):
    p1 = optional(str)

class C(Context):
    p2 = requires(int)

class D(Context):
    p2 = requires(str)

# --------------------------------------------------------------------

class TestDesign(unittest.TestCase):

    def testContext(self):
        a = A()
        self.assertIsInstance(a, Context)
        self.assertIsInstance(a, A)
        self.assertIsInstance(a, B)
        self.assertIsInstance(a, C)
        self.assertNotIsInstance(a, D)
        self.assertFalse(B.p1 in a)

        self.assertRaises(AssertionError, setattr, a, 'p1', 12)
        a.p1 = 'astr'
        self.assertEqual(a.p1, 'astr')

        c = C()
        self.assertIsInstance(a, Context)
        self.assertNotIsInstance(c, A)
        self.assertIsInstance(c, B)
        self.assertNotIsInstance(c, D)
        self.assertIsInstance(c, C)

        self.assertRaises(AssertionError, setattr, c, 'p2', 'astr')
        c.p2 = 12
        self.assertEqual(c.p2, 12)

# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()

