'''
Created on Jun 1, 2012

@package: utilities
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Testing for the  classes utility.
'''

import unittest
from ally.support.util_sys import extend, validateTypeFor

# --------------------------------------------------------------------

class TestClass(unittest.TestCase):

    def testExtend(self):
        class A:

            def __init__(self):
                self.a = 'a'

        class B:

            def __init__(self):
                self.b = 'b'

        class C(A):

            def __init__(self):
                self.c = 'c'

        AB = extend(A, B)
        ab = AB()
        self.assertTrue(ab.a == 'a')
        self.assertTrue(ab.b == 'b')

        self.assertRaises(TypeError, extend, AB, C)

    def testPropertyValidated(self):
        class A:
            __slots__ = ('a',)

            def __init__(self):
                self.a = 1

        validateTypeFor(A, 'a', int)

        a = A()
        self.assertRaises(ValueError, setattr, a, 'a', 'ola')
        a.a = 12

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

