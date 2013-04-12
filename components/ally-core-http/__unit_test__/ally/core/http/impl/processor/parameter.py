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
from ally.core.http.impl.processor.parameter import ParameterHandler
from ally.core.impl.invoker import InvokerCall
from ally.core.spec.transform.support import SAMPLE
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
        decoder = ParameterHandler()
        ioc.initialize(decoder)

        service = typeFor(IService).service
        invoker = InvokerCall(Service(), service.calls['get'])

        resolve = decoder.decodeInvoker(invoker)
        context = dict(converter=ConverterPath(), normalizer=ConverterPath())

        args = {}
        self.assertTrue(resolve(path='offset', value='20', target=args, **context))
        self.assertTrue(resolve(path='limit', value='0', target=args, **context))
        self.assertEqual(args, {'limit': 0, 'offset': 20})

        args = {}
        self.assertTrue(resolve(path='name', value='Gabriel', target=args, **context))
        self.assertTrue(resolve(path='asc', value='name', target=args, **context))
        self.assertTrue(resolve(path='desc', value='when', target=args, **context))
        self.assertTrue('q' in args)
        q = args['q']
        self.assertIsInstance(q, QMainModel)
        assert isinstance(q, QMainModel)
        self.assertTrue(q.name.like == 'Gabriel')
        self.assertTrue(q.name.ascending == True and q.name.priority == 1)
        self.assertTrue(q.when.ascending == False and q.when.priority == 2)

        args = {}
        self.assertTrue(resolve(path='asc', value='name, when', target=args, **context))
        self.assertTrue('q' in args)
        q = args['q']
        self.assertIsInstance(q, QMainModel)
        assert isinstance(q, QMainModel)
        self.assertTrue(q.name.ascending == True and q.name.priority == 1)
        self.assertTrue(q.when.ascending == True and q.when.priority == 2)

        args = {}
        self.assertTrue(resolve(path='qa.name', value='Gabriel', target=args, **context))
        self.assertTrue(resolve(path='desc', value='qa.name', target=args, **context))
        self.assertTrue(resolve(path='qa.something', value='startAndEnd', target=args, **context))
        self.assertTrue(resolve(path='qa.something.until', value='until', target=args, **context))
        self.assertTrue('qa' in args)
        qa = args['qa']
        self.assertIsInstance(qa, QAModel)
        assert isinstance(qa, QAModel)
        self.assertTrue(qa.name.like == 'Gabriel')
        self.assertTrue(qa.name.ascending == False and q.name.priority == 1)
        self.assertTrue(qa.something.start == 'startAndEnd' and qa.something.end == 'startAndEnd')
        self.assertTrue(qa.something.until == 'until')

        args = {}
        self.assertFalse(resolve(path='mainId', value='not', target=args, **context))
        self.assertFalse(resolve(path='scheme', value='not', target=args, **context))
        self.assertFalse(resolve(path='locale', value='not', target=args, **context))
        self.assertFalse(resolve(path='another', value='not', target=args, **context))
        self.assertFalse(resolve(path='name.ascending', value='False', target=args, **context))
        self.assertFalse(resolve(path='qa.name.priority', value='1', target=args, **context))

        invoker = InvokerCall(Service(), service.calls['insert'])

        resolve = decoder.decodeInvoker(invoker)

        self.assertFalse(resolve(path='offset', value='20', target=args, **context))
        self.assertFalse(resolve(path='limit', value='0', target=args, **context))

    def testEncode(self):
        encoder = ParameterHandler()
        ioc.initialize(encoder)

        service = typeFor(IService).service
        invoker = InvokerCall(Service(), service.calls['get'])

        resolve = encoder.encodeInvoker(invoker)
        context = dict(converter=ConverterPath(), normalizer=ConverterPath())

        args = {'offset': 20, 'limit':0}
        self.assertEqual([('offset', '20'), ('limit', '0')], list(resolve(value=args, **context)))

        q = QMainModel(name='Gabriel')
        q.name.ascending = True
        q.name.priority = 1
        q.when.ascending = False
        q.when.priority = 2
        args = {'q': q}
        self.assertEqual([('name', 'Gabriel'), ('asc', 'name'), ('desc', 'when')], list(resolve(value=args, **context)))

        q = QMainModel()
        q.name.ascending = True
        q.name.priority = 1
        q.when.ascending = True
        q.when.priority = 2
        args = {'q': q}
        self.assertEqual([('asc', 'name,when')], list(resolve(value=args, **context)))

        qa = QAModel()
        qa.name.like = 'Gabriel'
        qa.name.ascending = False
        qa.name.priority = 1
        qa.something.start = 'startAndEnd'
        qa.something.end = 'startAndEnd'
        qa.something.until = 'until'
        args = {'qa': qa}
        self.assertEqual([('qa.something', 'startAndEnd'), ('qa.something.until', 'until'), ('qa.name', 'Gabriel'),
                          ('desc', 'qa.name')], list(resolve(value=args, **context)))

        args = {'offset': 20, 'limit':0, 'q': q, 'qa': qa}
        self.assertEqual([('qa.something', 'startAndEnd'), ('qa.something.until', 'until'), ('qa.name', 'Gabriel'),
                          ('offset', '20'), ('limit', '0'), ('asc', 'name'), ('desc', 'qa.name'), ('asc', 'when')],
                         list(resolve(value=args, **context)))

        self.assertTrue(len(resolve(value=SAMPLE, **context)) > 10)

        invoker = InvokerCall(Service(), service.calls['insert'])

        resolve = encoder.encodeInvoker(invoker)

        self.assertFalse(resolve(value=SAMPLE, **context))

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
