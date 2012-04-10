'''
Created on Jan 25, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the encoder and decoder text module.
'''

from .. import __setup__
from ..test_support import EncoderPathTest, EncoderGetObj
from .samples.api.article import Article
from .samples.api.article_type import ArticleType
from .samples.impl.article import ArticleService
from .samples.impl.article_type import ArticleTypeService
from ally.api.type import Iter, TypeNone, Type, typeFor
from ally.container import ioc, aop
from ally.core.spec.resources import ResourcesManager, Path
from ally.core.spec.server import Processors, Request, Response
import unittest

# --------------------------------------------------------------------

class TestEncoderText(unittest.TestCase):

    def testEncoder(self):
        assembly = ioc.open(aop.modulesIn(__setup__))
        get = assembly.processForPartialName
        try:
            services = get('services')
            assert isinstance(services, list)
            services.append(ArticleTypeService())
            services.append(ArticleService())

            resourcesManager = get('resourcesManager')
            assert isinstance(resourcesManager, ResourcesManager)

            converterPath = get('converterPath')

            encoder = get('encoder')
            assert isinstance(encoder, EncoderGetObj)

            processors = get('encoderProcessors')
            assert isinstance(processors, Processors)

            processorMeta = get('encoderCreateMetaProcessors')
            assert isinstance(processorMeta, Processors)

            processorText = get('encoderTextProcessors')
            assert isinstance(processorText, Processors)

            req, rsp = Request(), Response()
            rsp.contentConverter = converterPath
            rsp.encoderPath = EncoderPathTest(converterPath)
            rsp.objMeta = encoder.obj = None

            # Test None convert

            rsp.obj, rsp.objType = None, TypeNone
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article'])
            processors.newChain().process(req, rsp)
            self.assertTrue(encoder.obj == None)

            # Test Property convert

            rsp.obj, rsp.objType = 1, typeFor(Article.Id)
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article', '1'])
            processors.newChain().process(req, rsp)
            self.assertTrue(encoder.obj == {'href': 'Article/1', 'Id': '1'})

            rsp.obj, rsp.objType = 'The Name', typeFor(Article.Name)
            processors.newChain().process(req, rsp)
            self.assertTrue(encoder.obj == {'Name': 'The Name'})

            # Test Model convert

            a = Article()
            a.Id, a.Name, a.Type = 1, 'Article 1', 2
            rsp.obj, rsp.objType = a, typeFor(Article)
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article', '1'])
            processors.newChain().process(req, rsp)
            self.assertEqual(encoder.obj,
                    {'Type': {'href': 'ArticleType/2', 'Id': '2'}, 'Id': '1', 'Name': 'Article 1'})

#            processorMeta.newChain().process(req, rsp)
#            del rsp.objMeta['Type']
#            processorText.newChain().process(req, rsp)
#            self.assertTrue(encoder.obj == {'Id': '1', 'Name': 'Article 1'})
#
#            processorMeta.newChain().process(req, rsp)
#            del rsp.objMeta['Name']
#            processorText.newChain().process(req, rsp)
#            self.assertTrue(encoder.obj == {'Type': {'href': 'ArticleType/2', 'Id': '2'}, 'Id': '1'})
#            
#            processorMeta.newChain().process(req, rsp)
#            del rsp.objMeta['Type']
#            del rsp.objMeta['Name']
#            processorText.newChain().process(req, rsp)
#            self.assertTrue(encoder.obj == {'Id': '1'})

            a = Article()
            a.Id, a.Name, a.Type = 3, 'Article 3', 4
            rsp.obj, rsp.objType = a, typeFor(Article)
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article', '1'])
            processors.newChain().process(req, rsp)
            self.assertTrue(encoder.obj ==
                    {'Type': {'href': 'ArticleType/4', 'Id': '4'}, 'Id': '3', 'Name': 'Article 3'})

            at = ArticleType()
            at.Id, at.Name = 1, 'Article Type 1'
            rsp.obj, rsp.objType = at, typeFor(ArticleType)
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['ArticleType', '1'])
            processors.newChain().process(req, rsp)
            self.assertTrue(encoder.obj ==
            {'Article': {'href': 'ArticleType/1/Article'}, 'Id': '1', 'Name': 'Article Type 1'})

            # Test list paths convert

            rsp.obj, rsp.objType = resourcesManager.findGetAllAccessible(), Iter(Type(Path))
            processors.newChain().process(req, rsp)
            self.assertEqual(encoder.obj,
                             {'Resources': [{'ArticleType': {'href': 'ArticleType'}}, {'Article': {'href': 'Article'}}]})

            # Test list property convert

            rsp.obj, rsp.objType = [1, 2], Iter(Article.Id)
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article'])
            processors.newChain().process(req, rsp)
            self.assertEqual(encoder.obj,
                            {'ArticleList':[{'href': 'Article/1', 'Id': '1'}, {'href': 'Article/2', 'Id': '2'}]})

            rsp.obj, rsp.objType = [1, 2], Iter(Article.Type)
            processors.newChain().process(req, rsp)
            self.assertEqual(encoder.obj,
                             {'ArticleList': [{'Type': {'href': 'ArticleType/1', 'Id': '1'}},
                                              {'Type': {'href': 'ArticleType/2', 'Id': '2'}}]})

            rsp.obj, rsp.objType = ['The Hulk 1', 'The Hulk 2'], Iter(Article.Name)
            processors.newChain().process(req, rsp)
            self.assertEqual(encoder.obj, {'ArticleList':[{'Name': 'The Hulk 1'}, {'Name': 'The Hulk 2'}]})

            # Test list models convert

            a1, a2 = Article(), Article()
            a1.Id, a1.Name, a1.Type = 1, 'Article 1', 1
            a2.Id, a2.Name, a2.Type = 2, 'Article 2', 2
            rsp.obj, rsp.objType = (a1, a2), Iter(Article)
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article'])
            processors.newChain().process(req, rsp)
            self.assertEqual(encoder.obj,
        {'ArticleList':
        [{'Type': {'href': 'ArticleType/1', 'Id': '1'}, 'Id': '1', 'href': 'Article/1', 'Name': 'Article 1'},
         {'Type': {'href': 'ArticleType/2', 'Id': '2'}, 'Id': '2', 'href': 'Article/2', 'Name': 'Article 2'}]})
        finally: ioc.close()

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
