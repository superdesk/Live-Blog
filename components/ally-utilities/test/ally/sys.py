'''
Created on Jun 1, 2012

@package: utilities
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Testing for the  classes utility.
'''

import unittest
from ally.support.util_sys import validateTypeFor

# --------------------------------------------------------------------

class TestSys(unittest.TestCase):

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

