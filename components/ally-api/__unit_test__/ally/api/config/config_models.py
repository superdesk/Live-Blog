'''
Created on May 29, 2011

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the decorated models.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally.api.config import model, query
from ally.api.criteria import AsOrdered, AsLikeOrdered
from ally.api.operator.container import Model
from ally.api.operator.descriptor import Reference
from ally.api.operator.type import TypeModel
from ally.api.type import typeFor
import unittest

# --------------------------------------------------------------------

@model(id='Id')
class Entity(object):

    Id = str

    X = float

@model
class APIModel(Entity):

    Y = str

    Entity = Entity

    EntitySecond = Entity

@model
class ExtendModel(APIModel):

    K = float

# --------------------------------------------------------------------

@query(Entity)
class TestQuery:

    date = AsOrdered

    name = AsLikeOrdered

    age = AsOrdered

    def __init__(self): pass #Just to have proper type hinting for criteria

# --------------------------------------------------------------------

class TestConfigure(unittest.TestCase):

    def testSuccesModel(self):
        a = APIModel()

        modelType = typeFor(APIModel)
        self.assertTrue(isinstance(modelType, TypeModel))
        m = modelType.container
        assert isinstance(m, Model)

        self.assertTrue(len(m.properties) == 5)
        self.assertTrue(APIModel.X not in a)
        self.assertTrue(a.X == None)
        a.X = None
        self.assertTrue(APIModel.X in a)
        self.assertTrue(a.X == None)
        self.assertTrue(isinstance(APIModel.X, Reference))
        a.X = 100
        self.assertTrue(a.X == 100)
        a.X = 101.2
        self.assertTrue(a.X == 101.2)

        self.assertTrue(APIModel.Y not in a)
        a.Y = 'heloo'
        self.assertTrue(APIModel.Y in a)
        self.assertTrue(a.Y == 'heloo')
        self.assertTrue(typeFor(APIModel.Y).type.isOf(str))
        del a.Y
        self.assertTrue(a.Y == None)

        self.assertTrue(typeFor(APIModel.Entity).type == typeFor(Entity))
        self.assertTrue(typeFor(APIModel.Entity.Id).type.isOf(str))
        self.assertTrue(APIModel.Entity not in a)
        a.Entity = '121'
        self.assertTrue(APIModel.Entity in a)
        self.assertTrue(isinstance(a.Entity, str))
        self.assertTrue(a.Entity == '121')
        del a.Entity
        self.assertTrue(a.Entity == None)

    def testSuccesQuery(self):
        q = TestQuery()

        self.assertTrue(TestQuery.age not in q)
        self.assertTrue(TestQuery.age.ascending not in q)
        self.assertTrue(q.age.ascending == None)
        self.assertTrue(TestQuery.age in q)
        self.assertTrue(TestQuery.age.ascending not in q)
        q.age.ascending = True
        q.age.priority = 1
        self.assertTrue(TestQuery.age.ascending in q)
        self.assertTrue(TestQuery.age.priority in q)
        self.assertTrue(q.age.priority == 1)
        self.assertTrue(q.date.ascending == None)
        q.date.orderAsc()
        self.assertTrue(q.date.ascending == True)
        q.name.like = 'heloo'
        self.assertTrue(q.name.like == 'heloo')
        del q.name.like
        self.assertTrue(TestQuery.name.like not in q)
        self.assertTrue(q.name.like == None)
        q.name.orderAsc()
        self.assertTrue(q.name.ascending == True)

# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()
