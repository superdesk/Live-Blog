'''
Created on Aug 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the operators listener binders.
'''

from ally.api.configure import APIModel as model, APICall as call, \
    APIService as service, modelFor
from ally.container.proxy import createProxy, ProxyWrapper
from ally.exception import InputException
from ally.listener.binder_op import validateAutoId, validateMaxLength, \
    validateManaged, validateModelProperties, bindValidations, \
    validateRequired, createModelMapping
import unittest

# --------------------------------------------------------------------

@model()
class Entity(object):
    
    id = str
    required = str
    withLength = str
    managed = str

@service()
class IServiceEntity:

    @call()
    def update(self, entity:Entity) -> str:
        '''
        '''
    
    @call()
    def insert(self, entity:Entity) -> str:
        '''
        '''
    
class DummyServiceEntity(IServiceEntity):
    
    def __init__(self): pass
    
    def update(self, entity):
        '''
        '''
        return 'updated'
    
    def insert(self, entity):
        '''
        '''
        return 'inserted'
        
# --------------------------------------------------------------------

class TestBinderOp(unittest.TestCase):
    
    def testValidation(self):
        EntityM = createModelMapping(Entity)

        validateAutoId(EntityM.id)
        validateRequired(EntityM.required)
        validateMaxLength(EntityM.withLength, 5)
        validateManaged(EntityM.managed)
        
        validateModelProperties(EntityM)
        
        proxySrv = createProxy(IServiceEntity)(ProxyWrapper(DummyServiceEntity()))
        bindValidations(proxySrv, {modelFor(Entity):EntityM})
        assert isinstance(proxySrv, IServiceEntity)
        
        e = Entity()
        self.assertRaisesRegex(InputException, "(Entity.required='Expected a value')", proxySrv.insert, e)
        self.assertRaisesRegex(InputException, "(Entity.id='Expected a value')", proxySrv.update, e)
        
        e.id = 'custom id'
        self.assertRaisesRegex(InputException, "(Entity.id='No value expected')", proxySrv.insert, e)
        self.assertTrue(proxySrv.update(e) == 'updated')
        
        e = Entity()
        e.required = 'Provided a value'
        self.assertTrue(proxySrv.insert(e) == 'inserted')
        e.id = 'id'
        self.assertTrue(proxySrv.update(e) == 'updated')
        
        e = Entity()
        e.required = 'required'
        e.withLength = 'This is a longer text then 5'
        self.assertRaisesRegex(InputException, "(Entity.withLength='Maximum length allowed is 5)", proxySrv.insert, e)
        e.withLength = 'hello'
        self.assertTrue(proxySrv.insert(e) == 'inserted')
        e.withLength = 'This is a longer text then 5'
        e.id = 'id'
        self.assertRaisesRegex(InputException, "(Entity.withLength='Maximum length allowed is 5)", proxySrv.update, e)
        e.withLength = 'hello'
        self.assertTrue(proxySrv.update(e) == 'updated')
        
        e = Entity()
        e.required = 'required'
        e.managed = 'should not have value'
        self.assertRaisesRegex(InputException, "(Entity.managed='No value expected')", proxySrv.insert, e)
        e.id = 'id'
        self.assertRaisesRegex(InputException, "(Entity.managed='No value expected')", proxySrv.update, e)
        
# --------------------------------------------------------------------
  
if __name__ == '__main__':
    unittest.main()
