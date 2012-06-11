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
from ally.core.spec.meta import IMetaDecode, IMetaEncode, SAMPLE
from ally.core.spec.resources import ConverterPath, Converter
import unittest
from collections import deque
from ally.core.impl.meta.encode import EncodeJoin, EncodeExploded, \
    EncodeJoinIndentifier
from ally.support.util_design import Context

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

        metaDecode = modelService.createDecode(Context(modelType=typeFor(ModelId)))
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

        metaEncode = modelService.createEncode(Context(modelType=typeFor(ModelId)))
        self.assertIsInstance(metaEncode, IMetaEncode)

        # We wrap the encode with explode and join in order to be able to validate results.
        metaEncode = EncodeJoinIndentifier(EncodeJoin(EncodeExploded(metaEncode), ','), '/')

        context = Context(converter=Converter(), converterId=ConverterPath(), normalizer=ConverterPath())

        model = ModelId()
        model.Id = 12
        self.assertEqual([('ModelId/Id', '12')],
                         [(m.identifier, m.value) for m in metaEncode.encode(model, context).items])

        model.ModelKey = 'The key'
        self.assertEqual([('ModelId/Id', '12'), ('ModelId/ModelKey', 'The key')],
                         [(m.identifier, m.value) for m in metaEncode.encode(model, context).items])

        model.Name = 'Uau Name'
        model.Flags = ['1', '2', '3']
        self.assertEqual([('ModelId/Id', '12'), ('ModelId/Name', 'Uau Name'), ('ModelId/Flags/Value', '1'),
                          ('ModelId/Flags/Value', '2'), ('ModelId/Flags/Value', '3'), ('ModelId/ModelKey', 'The key')],
                         [(m.identifier, m.value) for m in metaEncode.encode(model, context).items])

        metaEncode = modelService.createEncode(Context(modelType=typeFor(List(ModelId))))
        self.assertIsInstance(metaEncode, IMetaEncode)

        # We wrap the encode with explode and join in order to be able to validate results.
        metaEncode = EncodeJoinIndentifier(EncodeJoin(EncodeExploded(metaEncode), ','), '/')

        model = [model]
        self.assertEqual([('ModelIdList/ModelId/Id', '12'), ('ModelIdList/ModelId/Name', 'Uau Name'),
                          ('ModelIdList/ModelId/Flags/Value', '1'), ('ModelIdList/ModelId/Flags/Value', '2'),
                          ('ModelIdList/ModelId/Flags/Value', '3'), ('ModelIdList/ModelId/ModelKey', 'The key')],
                         [(m.identifier, m.value) for m in metaEncode.encode(model, context).items])

        self.assertTrue([(m.identifier, m.value) for m in metaEncode.encode(SAMPLE, context).items])


# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
