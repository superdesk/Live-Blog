'''
Created on Jun 9, 2011

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the API authentication types module.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

import unittest
from ally.api.config import model
from ally.api.authentication import auth
from ally.api.type import typeFor
from ally.api.operator.authentication.type import IAuthenticated

# --------------------------------------------------------------------

@model(id='Key')
class Model1:
    Key = str
    Name = str

@model(id='Id')
class Model2:
    Id = int
    Model1 = auth(Model1)

# --------------------------------------------------------------------

class TestType(unittest.TestCase):

    def testEquality(self):
        self.assertEqual(typeFor(Model1), typeFor(Model2.Model1).type)
        self.assertIsInstance(typeFor(Model2.Model1).type, IAuthenticated)

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
