'''
Created on Mar 20, 2012

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the decorated services.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from .config_models import Entity, APIModel
from ally.api.config import service, call, GET
from ally.api.type import Integer, Number, String
import unittest

# --------------------------------------------------------------------

@service
class IServiceEntity:

    @call(Number, Entity.X, method=GET)
    def multipy(self, x=None):
        '''
        '''

@service((Entity, APIModel))
class IService(IServiceEntity):

    @call(None, Number, method=GET)
    def doNothing(self, x):
        '''
        '''

    @call(method=GET)
    def intToStr(self, x:Integer) -> String:
        '''
        '''

# --------------------------------------------------------------------

class ServiceImpl(IService):

    def multipy(self, x=None):
        if x is None:
            return 100000
        return x + x

    def intToStr(self, x):
        return str(x)

    def doNothing(self, x):
        pass

    def implCustom(self):
        '''
        '''

# --------------------------------------------------------------------

class TestConfigure(unittest.TestCase):

    def testSuccesServiceCalls(self):
        s = ServiceImpl()

        self.assertTrue(s.multipy() == 100000)
        self.assertTrue(s.multipy(23) == 46)
        self.assertTrue(s.multipy(15.5) == 31)
        self.assertTrue(s.intToStr(23) == '23')
        self.assertTrue(s.intToStr(11) == '11')
        self.assertTrue(s.doNothing(11) == None)

    def testFailedServiceCalls(self):
        class ServiceImpl(IService):

            def multipy(self, x=None):
                if x is None:
                    return 100000
                return x + x

            def intToStr(self, x):
                return str(x)

        self.assertRaises(TypeError, ServiceImpl)

# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()
