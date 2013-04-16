'''
Created on Aug 24, 2011

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the operators listener binders.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally.api.config import model, service, call
from ally.container.binder_op import validateAutoId, validateMaxLength, \
    validateManaged, bindValidations, validateRequired
from ally.container.impl.proxy import proxyWrapFor
from ally.exception import InputError
import unittest

# --------------------------------------------------------------------

@model(id='Id')
class Entity:

    Id = str
    Required = str
    WithLength = str
    Managed = str

@service
class IServiceEntity:

    @call
    def update(self, entity:Entity) -> str:
        '''
        '''

    @call
    def insert(self, entity:Entity) -> str:
        '''
        '''

class DummyServiceEntity(IServiceEntity):

    def update(self, entity):
        '''
        '''
        return 'updated'

    def insert(self, entity):
        '''
        '''
        return 'inserted'

    def _hidden(self):
        return 'Hidden'

# --------------------------------------------------------------------

class TestBinderOp(unittest.TestCase):

    def testValidation(self):
        Entity._ally_listeners = {}

        validateAutoId(Entity.Id)
        validateRequired(Entity.Required)
        validateMaxLength(Entity.WithLength, 5)
        validateManaged(Entity.Managed)

        dummyService = DummyServiceEntity()
        proxySrvNonValid = proxyWrapFor(dummyService)
        proxySrv = proxyWrapFor(dummyService)
        bindValidations(proxySrv)
        assert isinstance(proxySrv, IServiceEntity)

        e = Entity()
        self.assertRaisesRegex(InputError, "(Entity.Required='Expected a value')", proxySrv.insert, e)
        self.assertEqual(proxySrvNonValid.insert(e), 'inserted')
        self.assertRaisesRegex(InputError, "(Entity.Id='Expected a value')", proxySrv.update, e)
        self.assertEqual(proxySrvNonValid.update(e), 'updated')

        e.Id = 'custom id'
        self.assertRaisesRegex(InputError, "(Entity.Id='No value expected')", proxySrv.insert, e)
        self.assertTrue(proxySrv.update(e) == 'updated')

        e = Entity()
        e.Required = 'Provided a value'
        self.assertTrue(proxySrv.insert(e) == 'inserted')
        e.Id = 'id'
        self.assertTrue(proxySrv.update(e) == 'updated')

        e = Entity()
        e.Required = 'required'
        e.WithLength = 'This is a longer text then 5'
        self.assertRaisesRegex(InputError, "(Entity.WithLength='Maximum length allowed is 5)", proxySrv.insert, e)
        e.WithLength = 'hello'
        self.assertTrue(proxySrv.insert(e) == 'inserted')
        e.WithLength = 'This is a longer text then 5'
        e.Id = 'id'
        self.assertRaisesRegex(InputError, "(Entity.WithLength='Maximum length allowed is 5)", proxySrv.update, e)
        e.WithLength = 'hello'
        self.assertTrue(proxySrv.update(e) == 'updated')

        e = Entity()
        e.Required = 'required'
        e.Managed = 'should not have value'
        self.assertRaisesRegex(InputError, "(Entity.Managed='No value expected')", proxySrv.insert, e)
        e.Id = 'id'
        self.assertRaisesRegex(InputError, "(Entity.Managed='No value expected')", proxySrv.update, e)

        self.assertRaises(AttributeError, getattr, proxySrv, '_hidden')

# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()
