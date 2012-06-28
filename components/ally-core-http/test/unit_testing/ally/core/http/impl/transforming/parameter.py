'''
Created on May 21, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides testing for the parameters.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally.api.config import model, query, service, call
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered, AsRange, AsEqual
from ally.api.type import typeFor, Locale, List, Scheme
from ally.container import ioc
from ally.core.http.impl.transforming.parameter import ParameterTransformer
from ally.core.impl.invoker import InvokerCall
from ally.core.impl.meta.general import Conversion
from ally.core.spec.resources import ConverterPath
from ally.design.exploit import Exploit, Resolve
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

    @call
    def insert(self, main:MainModel) -> MainModel.Id:
        '''
        Nothing.
        '''

class Service(IService):

    def get(self, mainId, scheme, locale, another=None, q=None, qa=None, offset=0, limit=None):
        pass

    def insert(self, main):
        pass

# --------------------------------------------------------------------

class TestParameter(unittest.TestCase):

    def testDecode(self):
        transformer = ParameterTransformer()
        ioc.initialize(transformer)

        service = typeFor(IService).service
        for call in service.calls:
            if call.name == 'get': break
        invoker = InvokerCall(Service(), call)

        resolve = Resolve(transformer.createDecode(invoker))
        context = dict(converter=ConverterPath(), normalizer=ConverterPath())

        args = {}
        self.assertTrue(resolve.request('offset', value='20', target=args, **context))
        self.assertTrue(resolve.request('limit', value='0', target=args, **context))
        self.assertTrue(resolve.doAll())
        self.assertEqual(args, {'limit': 0, 'offset': 20})

        args = {}
        self.assertTrue(resolve.request('name', value='Gabriel', target=args, **context))
        self.assertTrue(resolve.request('asc', value='name', target=args, **context))
        self.assertTrue(resolve.request('desc', value='when', target=args, **context))
        self.assertTrue(resolve.doAll())
        self.assertTrue('q' in args)
        q = args['q']
        self.assertIsInstance(q, QMainModel)
        assert isinstance(q, QMainModel)
        self.assertTrue(q.name.like == 'Gabriel')
        self.assertTrue(q.name.ascending == True and q.name.priority == 1)
        self.assertTrue(q.when.ascending == False and q.when.priority == 2)

        args = {}
        self.assertTrue(resolve.request('asc', value='name, when', target=args, **context))
        self.assertTrue(resolve.doAll())
        self.assertTrue('q' in args)
        q = args['q']
        self.assertIsInstance(q, QMainModel)
        assert isinstance(q, QMainModel)
        self.assertTrue(q.name.ascending == True and q.name.priority == 1)
        self.assertTrue(q.when.ascending == True and q.when.priority == 2)

        args = {}
        self.assertTrue(resolve.request('qa.name', value='Gabriel', target=args, **context))
        self.assertTrue(resolve.request('desc', value='qa.name', target=args, **context))
        self.assertTrue(resolve.request('qa.something', value='startAndEnd', target=args, **context))
        self.assertTrue(resolve.request('qa.something.until', value='until', target=args, **context))
        self.assertTrue(resolve.doAll())
        self.assertTrue('qa' in args)
        qa = args['qa']
        self.assertIsInstance(qa, QAModel)
        assert isinstance(qa, QAModel)
        self.assertTrue(qa.name.like == 'Gabriel')
        self.assertTrue(qa.name.ascending == False and q.name.priority == 1)
        self.assertTrue(qa.something.start == 'startAndEnd' and qa.something.end == 'startAndEnd')
        self.assertTrue(qa.something.until == 'until')

        args = {}
        self.assertFalse(resolve.request('mainId', value='not', target=args, **context))
        self.assertFalse(resolve.request('scheme', value='not', target=args, **context))
        self.assertFalse(resolve.request('locale', value='not', target=args, **context))
        self.assertFalse(resolve.request('another', value='not', target=args, **context))
        self.assertFalse(resolve.request('name.ascending', value='False', target=args, **context))
        self.assertFalse(resolve.request('qa.name.priority', value='1', target=args, **context))

        for call in service.calls:
            if call.name == 'insert': break
        invoker = InvokerCall(Service(), call)

        resolve = Resolve(transformer.createDecode(invoker))

        self.assertFalse(resolve.request('offset', value='20', target=args, **context))
        self.assertFalse(resolve.request('limit', value='0', target=args, **context))
#
#    def testEncode(self):
#        handler = ParameterHandler()
#        ioc.initialize(handler)
#
#        service = typeFor(IService).service
#        for call in service.calls:
#            if call.name == 'get': break
#        invoker = InvokerCall(Service(), call)
#
#        metaEncode = handler.createEncode(invoker)
#        self.assertIsInstance(metaEncode, IMetaEncode)
#
#        context = Conversion()
#        context.converter = ConverterPath()
#        context.normalizer = ConverterPath()
#
#        args = {'offset': 20, 'limit':0}
#        self.assertEqual([('offset', '20'), ('limit', '0')],
#                         [(m.identifier, m.value) for m in metaEncode.encode(args, context).items])
#
#        q = QMainModel(name='Gabriel')
#        q.name.ascending = True
#        q.name.priority = 1
#        q.when.ascending = False
#        q.when.priority = 2
#        args = {'q': q}
#        self.assertEqual([('name', 'Gabriel'), ('asc', 'name'), ('desc', 'when')],
#                         [(m.identifier, m.value) for m in metaEncode.encode(args, context).items])
#
#        q = QMainModel()
#        q.name.ascending = True
#        q.name.priority = 1
#        q.when.ascending = True
#        q.when.priority = 2
#        args = {'q': q}
#        self.assertEqual([('asc', 'name,when')],
#                         [(m.identifier, m.value) for m in metaEncode.encode(args, context).items])
#
#        qa = QAModel()
#        qa.name.like = 'Gabriel'
#        qa.name.ascending = False
#        qa.name.priority = 1
#        qa.something.start = 'startAndEnd'
#        qa.something.end = 'startAndEnd'
#        qa.something.until = 'until'
#        args = {'qa': qa}
#        self.assertEqual([('qa.something', 'startAndEnd'), ('qa.something.until', 'until'), ('qa.name', 'Gabriel'),
#                          ('desc', 'qa.name')],
#                         [(m.identifier, m.value) for m in metaEncode.encode(args, context).items])
#
#        args = {'offset': 20, 'limit':0, 'q': q, 'qa': qa}
#        self.assertEqual([('offset', '20'), ('limit', '0'), ('qa.something', 'startAndEnd'),
#                          ('qa.something.until', 'until'), ('qa.name', 'Gabriel'), ('asc', 'name'), ('desc', 'qa.name'),
#                          ('asc', 'when')],
#                         [(m.identifier, m.value) for m in metaEncode.encode(args, context).items])
#
#        self.assertTrue([(m.identifier, m.value) for m in metaEncode.encode(SAMPLE, context).items])
#
#        for call in service.calls:
#            if call.name == 'insert': break
#        invoker = InvokerCall(Service(), call)
#
#        metaEncode = handler.createEncode(invoker)
#        self.assertIsInstance(metaEncode, IMetaEncode)
#
#        self.assertTrue(metaEncode.encode(SAMPLE, context) is None)

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
