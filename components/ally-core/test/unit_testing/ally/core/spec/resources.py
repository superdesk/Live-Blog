'''
Created on Jun 21, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Resources testing.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally.api.type import Boolean, typeFor, Integer
from ally.core.spec.resources import Converter
import unittest

# --------------------------------------------------------------------

class TestConversion(unittest.TestCase):

    def testConversion(self):
        converter = Converter()

        self.assertEqual(converter.asValue('10', typeFor(Integer)), 10)
        self.assertEqual(converter.asValue('false', typeFor(Boolean)), False)

# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()
