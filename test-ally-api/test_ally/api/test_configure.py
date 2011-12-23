'''
Created on May 29, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the decorator module.
'''
from ally.api.operator import GET
from ally.api.criteria import AsOrdered, AsLike
from ally.api.configure import APIModel as model, APIService as service, \
    APICall as call, APIQuery as query, \
    propertiesFor
from ally.api.type import Integer, Number, String, Type
import sys
import unittest

# --------------------------------------------------------------------

@model()
class Entity(object):
    
    id = str
    
    x = float

@model()
class APIModel(Entity):
        
    y = str
    
    entity = Entity.id
        
    entitySecond = Entity.id

@model()
class ExtendModel(APIModel):
    
    k = float
    
# --------------------------------------------------------------------


@query()
class TestQuery:
    
    date = AsOrdered
    
    name = AsLike
    
    age = AsOrdered
    
    def __init__(self): pass #Just to have proper type hinting for criteria

# --------------------------------------------------------------------

@service()
class IServiceEntity:

    @call(Number, Entity.x, method=GET)
    def multipy(self, x=None):
        '''
        '''
        
@service((Entity, APIModel))
class IService(IServiceEntity):
        
    @call(None, Number, method=GET)
    def doNothing(self, x):
        '''
        '''
        
    @call(String, Integer, method=GET)
    def intToStr(self, x):
        '''
        '''

    def undecorated(self):
        '''
        '''
        
@service()
class IServiceModule:
    
    @call(int, String, method=GET)
    def failing(self, x):
        '''
        '''

# --------------------------------------------------------------------

class ServiceImpl:

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

def failing(x):
    return 'Fail for ' + str(x)
       
# --------------------------------------------------------------------

class TestConfigure(unittest.TestCase):
        
    def testSuccesProperties(self):
        a = APIModel()

        self.assertTrue(len(propertiesFor(a).properties) == 5)
        self.assertTrue(a.x == None)
        a.x = None
        self.assertTrue(a.x == None)
        self.assertTrue(isinstance(APIModel.x, Type))
        a.x = 100
        self.assertTrue(a.x == 100)
        a.x = 101.2
        self.assertTrue(a.x == 101.2)
        a.y = 'heloo'
        self.assertTrue(a.y == 'heloo')
        self.assertTrue(APIModel.y.property.type.forClass() == str)
        del a.y
        self.assertTrue(a.y == None)
        a.entity = '100'
        self.assertTrue(isinstance(a.entity, str))
        del a.entity
        self.assertTrue(a.entity == None)

    def testSuccesCondition(self):
        q = TestQuery()

        self.assertTrue(q.age.orderAscending == None)
        q.age.orderAscending = True
        self.assertTrue(q.age.index() == 1)
        self.assertTrue(q.date.orderAscending == None)
        q.date.orderAsc()
        self.assertTrue(q.date.orderAscending == True)
        self.assertTrue(q.date.index() == 2)
        q.name.like = 'heloo'
        self.assertTrue(q.name.like == 'heloo')
        del q.name.like
        self.assertTrue(q.name.like == None)
        q.name.orderAsc()
        self.assertTrue(q.name.orderAscending == True)
        self.assertTrue(q.name.index() == 3)
    
    # ----------------------------------------------------------------
    
    def testFailedProperties(self):
        a = APIModel()

        self.assertRaises(AssertionError, a.__setattr__, 'x', 'nu')
        self.assertRaises(AssertionError, a.__setattr__, 'x', (100, 3))
        self.assertRaises(AssertionError, a.__setattr__, 'y', 1000.0)
        self.assertRaises(AssertionError, a.__setattr__, 'entity', 1000)
    
    def testSuccesServiceCalls(self):
        s = IService(ServiceImpl())
        
        self.assertTrue(s.multipy() == 100000)
        self.assertTrue(s.multipy(23) == 46)
        self.assertTrue(s.multipy(15.5) == 31)
        self.assertTrue(s.intToStr(23) == '23')
        self.assertTrue(s.intToStr(11) == '11')
        self.assertTrue(s.doNothing(11) == None)

    # ----------------------------------------------------------------
        
    def testFailedServiceCalls(self):
        s = IService(ServiceImpl())
        
        self.assertRaises(AssertionError, s.intToStr, 11.2)
        self.assertRaises(AssertionError, s.multipy, '12')
        self.assertRaises(AssertionError, s.multipy, s)
        
        s = IServiceModule(sys.modules[__name__])
        self.assertRaises(AssertionError, s.failing, 12)
        self.assertRaises(AssertionError, s.failing, '13')
        
# --------------------------------------------------------------------
  
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
