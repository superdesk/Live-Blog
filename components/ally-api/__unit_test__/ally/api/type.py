'''
Created on Jun 9, 2011

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the API types module.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally import type_legacy as numbers
from ally.api.type import Number, Integer, String, Type, Boolean, typeFor, \
    TypeSupport
import unittest

# --------------------------------------------------------------------

class TestType(unittest.TestCase):

    def testSuccesBoolean(self):
        bt = typeFor(Boolean)

        self.assertTrue(isinstance(bt, Type))
        self.assertTrue(bt.isOf(bool))
        self.assertTrue(bt.isValid(True))

        bt = typeFor(bool)

        self.assertTrue(bt.isValid(False))
        self.assertTrue(bt.isValid(True))

    def testSuccesInt(self):
        it = typeFor(Integer)

        self.assertTrue(isinstance(it, Type))
        self.assertTrue(it.isOf(int))
        self.assertTrue(it.isValid(100))

        it = typeFor(int)

        self.assertTrue(it.isValid(-12))
        self.assertTrue(it.isValid(0))

    def testSuccesNumber(self):
        nt = typeFor(Number)

        self.assertTrue(isinstance(nt, Type))
        self.assertTrue(nt.isOf(numbers.Number))
        self.assertTrue(nt.isValid(100))

        nt = typeFor(float)

        self.assertTrue(nt.isValid(100.12))

        nt = typeFor(numbers.Number)

        self.assertTrue(nt.isValid(-1.12))

    def testSuccesStr(self):
        st = typeFor(String)

        self.assertTrue(isinstance(st, Type))
        self.assertTrue(st.isOf(str))
        self.assertTrue(st.isValid('ugu'))

        st = typeFor(str)

        self.assertTrue(st.isValid("heloo world"))
        self.assertTrue(st.isValid('Moi'))

    def testSuccessContainer(self):
        class TypeContainer1:

            _ally_type = typeFor(Boolean)

        class TypeContainer2:

            def __init__(self):
                self._ally_type = typeFor(Boolean)


        self.assertTrue(isinstance(TypeContainer1, TypeSupport))
        container2 = TypeContainer2()
        self.assertTrue(isinstance(container2, TypeSupport))

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

    def testFailedContainer(self):
        self.assertFalse(isinstance(TestType, TypeSupport))
        container2 = object()
        self.assertFalse(isinstance(container2, TypeSupport))

# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()
