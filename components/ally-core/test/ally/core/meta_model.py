'''
Created on May 21, 2012

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides testing for the parameters decoding.
'''

from ally.api.config import model
from ally.api.type import typeFor, List
from ally.container import ioc
from ally.core.impl.meta.model import ModelMetaService
from ally.core.spec.meta import IMetaDecode, Context, IMetaEncode
from ally.core.spec.resources import ConverterPath, Converter
import unittest
from collections import deque
from ally.core.impl.meta.encode import EncodeObjectExploded, EncodeJoin

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
        modelService = ModelMetaService()
        ioc.initialize(modelService)

        metaDecode = modelService.createDecode(Context(type=typeFor(ModelId)))
        self.assertIsInstance(metaDecode, IMetaDecode)

        context = Context(converter=Converter(), converterId=ConverterPath(), normalizer=ConverterPath())

        models = {}
        self.assertTrue(metaDecode.decode(deque(['ModelId', 'Id']), '20', models, context))
        self.assertTrue(metaDecode.decode(deque(['ModelId', 'Name']), 'A name', models, context))
        self.assertTrue(metaDecode.decode(deque(['ModelId', 'Flags']), 'Flag 1', models, context))
        self.assertTrue(metaDecode.decode(deque(['ModelId', 'Flags']), ['Flag 2', 'Flag 3'], models, context))
        self.assertTrue(metaDecode.decode(deque(['ModelId', 'ModelKey']), 'A Key', models, context))

        self.assertTrue(typeFor(ModelId) in models)
        m = models[typeFor(ModelId)]
        self.assertIsInstance(m, ModelId)
        assert isinstance(m, ModelId)
        self.assertTrue(m.Id == 20)
        self.assertTrue(m.Name == 'A name')
        self.assertTrue(m.Flags == ['Flag 1', 'Flag 2', 'Flag 3'])
        self.assertTrue(m.ModelKey == 'A Key')

    def testEncode(self):
        modelService = ModelMetaService()
        ioc.initialize(modelService)

        metaEncode = modelService.createEncode(Context(type=typeFor(ModelId)))
        self.assertIsInstance(metaEncode, IMetaEncode)

        # We wrap the encode with explode and join in order to be able to validate results.
        explode = EncodeObjectExploded()
        explode.properties.append(EncodeJoin(metaEncode, ','))
        metaEncode = explode

        context = Context(converter=Converter(), converterId=ConverterPath(), normalizer=ConverterPath())

        m = ModelId()
        m.Id = 12
        self.assertEqual([(['ModelId', 'Id'], '12')],
                         [(m.identifier, m.value) for m in metaEncode.encode(m, context).properties])

        m.ModelKey = 'The key'
        self.assertEqual([(['ModelId', 'Id'], '12'), (['ModelId', 'ModelKey'], 'The key')],
                         [(m.identifier, m.value) for m in metaEncode.encode(m, context).properties])

        m.Name = 'Uau Name'
        m.Flags = ['1', '2', '3']
        self.assertEqual([(['ModelId', 'Id'], '12'), (['ModelId', 'Name'], 'Uau Name'),
                          (['ModelId', 'Flags'], '1,2,3'), (['ModelId', 'ModelKey'], 'The key')],
                         [(m.identifier, m.value) for m in metaEncode.encode(m, context).properties])

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
