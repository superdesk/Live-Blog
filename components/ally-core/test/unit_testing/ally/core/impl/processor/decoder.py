'''
Created on Aug 23, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Model encoder testing.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally.api.config import model
from ally.api.operator.type import TypeModel
from ally.api.type import List, typeFor
from ally.container import ioc
from ally.core.impl.processor.decoder import CreateDecoderHandler
from ally.core.spec.resources import ConverterPath
from ally.exception import InputError
from collections import deque
import unittest

# --------------------------------------------------------------------

@model(id='Key')
class ModelKey:
    Key = str
    Name = str

@model(id='Id')
class ModelId:
    Id = int
    Name = str
    Flags = List(str)
    ModelKey = ModelKey

# --------------------------------------------------------------------

class TestModel(unittest.TestCase):

    def testDecode(self):
        transformer = CreateDecoderHandler()
        ioc.initialize(transformer)

        typeModel = typeFor(ModelId)
        assert isinstance(typeModel, TypeModel)
        resolve = transformer.decoderFor('model', typeModel)

        context = dict(converter=ConverterPath(), converterId=ConverterPath(), normalizer=ConverterPath())

        args = {}
        self.assertTrue(resolve(path=deque(('Id',)), value='12', target=args, **context))
        self.assertTrue('model' in args)
        m = args['model']
        self.assertIsInstance(m, ModelId)
        assert isinstance(m, ModelId)
        self.assertTrue(m.Id == 12)

        args = {}
        self.assertTrue(resolve(path=deque(('ModelId', 'Id')), value='23', target=args, **context))
        self.assertTrue('model' in args)
        m = args['model']
        self.assertIsInstance(m, ModelId)
        assert isinstance(m, ModelId)
        self.assertTrue(m.Id == 23)

        self.assertTrue(resolve(path=deque(('ModelKey', 'Key')), value='The key', target=args, **context))
        self.assertTrue(m.ModelKey == 'The key')

        self.assertTrue(resolve(path=deque(('Name',)), value='Uau Name', target=args, **context))
        self.assertTrue(resolve(path=deque(('Flags',)), value=['1', '2', '3'], target=args, **context))
        self.assertTrue(m.Name == 'Uau Name')
        self.assertTrue(m.Flags == ['1', '2', '3'])

        args = {}
        self.assertTrue(resolve(path=deque(('Flags',)), value='3', target=args, **context))
        self.assertTrue(resolve(path=deque(('Flags',)), value='1', target=args, **context))
        self.assertTrue(resolve(path=deque(('Flags',)), value='2', target=args, **context))
        self.assertTrue('model' in args)
        m = args['model']
        self.assertIsInstance(m, ModelId)
        self.assertTrue(m.Flags == ['3', '1', '2'])

        self.assertRaises(InputError, resolve, path=deque(('ModelKey', 'Name')), value='The name',
                          target=args, **context)

# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()
