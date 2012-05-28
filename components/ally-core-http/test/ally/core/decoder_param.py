'''
Created on May 21, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides testing for the parameters decoding.
'''

from ally.api.config import model, query, service, call
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered, AsRange, AsEqual
from ally.api.type import typeFor, Locale, List, Scheme
from ally.core.http.impl.meta.parameter import ParamMetaService
from ally.core.impl.invoker import InvokerCall
from ally.core.spec.meta import MetaDecode, Context
from ally.core.spec.resources import ConverterPath
import unittest

# --------------------------------------------------------------------

@model(id='Id')
class MainModel:
    Id = int

@model(id='Key')
class AModel:
    Key = str

@query(MainModel)
class QMainModel:
    name = AsLikeOrdered
    when = AsDateTimeOrdered

@query(AModel)
class QAModel:
    name = AsLikeOrdered
    something = AsRange
    equals = AsEqual

@service
class IService:

    @call
    def get(self, mainId:MainModel.Id, scheme:Scheme, locale:List(Locale), another:AModel.Key=None,
            q:QMainModel=None, qa:QAModel=None, offset:int=0, limit:int=None) -> MainModel:
        '''
        Nothing.
        '''

class Service(IService):

    def get(self, mainId, scheme, locale, another=None, q=None, qa=None, offset=0, limit=None):
        pass

# --------------------------------------------------------------------

class TestDecodeParam(unittest.TestCase):

    def testDecode(self):

        service = typeFor(IService).service
        for call in service.calls:
            if call.name == 'get': break
        invoker = InvokerCall(Service(), call)

        transform = ConverterPath()
        context = Context(converter=transform, normalizer=transform)
        metaService = ParamMetaService()

        metaDecode = metaService.createDecode(invoker)
        self.assertIsInstance(metaDecode, MetaDecode)

        args = {}
        self.assertTrue(metaDecode.decode('offset', '20', args, context))
        self.assertTrue(metaDecode.decode('limit', '0', args, context))
        self.assertEqual(args, {'limit': 0, 'offset': 20})

        args = {}
        self.assertTrue(metaDecode.decode('name', 'Gabriel', args, context))
        self.assertTrue(metaDecode.decode('asc', 'name', args, context))
        self.assertTrue(metaDecode.decode('desc', 'when', args, context))
        self.assertTrue('q' in args)
        q = args['q']
        self.assertIsInstance(q, QMainModel)
        assert isinstance(q, QMainModel)
        self.assertTrue(q.name.like == 'Gabriel')
        self.assertTrue(q.name.ascending == True and q.name.priority == 1)
        self.assertTrue(q.when.ascending == False and q.when.priority == 2)

        args = {}
        self.assertTrue(metaDecode.decode('qa.name', 'Gabriel', args, context))
        self.assertTrue(metaDecode.decode('desc', 'qa.name', args, context))
        self.assertTrue(metaDecode.decode('qa.something', 'startAndEnd', args, context))
        self.assertTrue(metaDecode.decode('qa.something.until', 'until', args, context))
        self.assertTrue('qa' in args)
        qa = args['qa']
        self.assertIsInstance(qa, QAModel)
        assert isinstance(qa, QAModel)
        self.assertTrue(qa.name.like == 'Gabriel')
        self.assertTrue(qa.name.ascending == False and q.name.priority == 1)
        self.assertTrue(qa.something.start == 'startAndEnd' and qa.something.end == 'startAndEnd')
        self.assertTrue(qa.something.until == 'until')

        args = {}
        self.assertFalse(metaDecode.decode('mainId', 'not', args, context))
        self.assertFalse(metaDecode.decode('scheme', 'not', args, context))
        self.assertFalse(metaDecode.decode('locale', 'not', args, context))
        self.assertFalse(metaDecode.decode('another', 'not', args, context))
        self.assertFalse(metaDecode.decode('name.ascending', 'False', args, context))
        self.assertFalse(metaDecode.decode('qa.name.priority', '1', args, context))

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
