'''
Created on Jun 13, 2012

@package: utilities
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Testing for the sys utility.
'''

import unittest

# --------------------------------------------------------------------

class TestDesign(unittest.TestCase):

    def testContext(self):
        from ally.design.context import Context, requires
        class A(Context):
            property1 = requires(str)
            property2 = requires(int)

        class B(Context):
            property1 = requires(str)

        class C(Context):
            property2 = requires(int)

        class D(Context):
            property2 = requires(str)

        a = A()
        self.assertIsInstance(a, A)
        self.assertIsInstance(a, B)
        self.assertIsInstance(a, C)
        self.assertNotIsInstance(a, D)

        self.assertRaises(AssertionError, setattr, a, 'property1', 12)
        a.property1 = 'astr'
        self.assertEqual(a.property1, 'astr')

        c = C()
        self.assertNotIsInstance(c, A)
        self.assertNotIsInstance(c, B)
        self.assertNotIsInstance(c, D)
        self.assertIsInstance(c, C)

        self.assertRaises(AssertionError, setattr, c, 'property2', 'astr')
        c.property2 = 12
        self.assertEqual(c.property2, 12)

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

