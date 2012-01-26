'''
Created on Jan 25, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the encoder and decoder text module.
'''

from .. import __setup__
from ..samples.api.article import Article
from ..samples.impl.article import ArticleService
from ..samples.impl.article_type import ArticleTypeService
from ally.api.configure import modelFor
from ally.api.type import TypeModel, Iter, TypeClass, TypeNone
from ally.container import ioc, aop
from ally.core.impl.processor.encdec_text import EncodingTextHandler
import unittest
from ally.core.spec.resources import ResourcesManager, Path
from ..samples.api.article_type import ArticleType

# --------------------------------------------------------------------

class TestEncDecText(unittest.TestCase):
        
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
            
            encoder = get('encoderText')
            assert isinstance(encoder, EncodingTextHandler)
            
            asString = lambda value, type: str(value)
            pathEncode = lambda path: '/'.join(path.toPaths(converterPath))
            
            # Test None convert
            kyargs = dict(vtype=TypeNone, asString=asString, pathEncode=pathEncode)
            kyargs['value'] = None
            
            self.assertTrue(encoder.convert(**kyargs) == None)
            
            # Test Property convert
            kyargs = dict(vtype=Article.Id, asString=asString, pathEncode=pathEncode)
            kyargs['value'] = 1
            kyargs['resourcePath'] = resourcesManager.findResourcePath(converterPath, ['Article', '1'])
            
            self.assertTrue(encoder.convert(**kyargs) == {'href': 'Article/1', 'Id': '1'})
            
            kyargs['value'] = 'The Name'
            kyargs['vtype'] = Article.Name
            self.assertTrue(encoder.convert(**kyargs) == {'Name': 'The Name'})
            
            # Test Model convert
            kyargs = dict(vtype=TypeModel(modelFor(Article)), asString=asString, pathEncode=pathEncode)
            
            a = Article()
            a.Id = 1
            a.Name = 'Article 1'
            a.Type = 2
            kyargs['value'] = a
            kyargs['resourcePath'] = resourcesManager.findResourcePath(converterPath, ['Article', '1'])
            
            self.assertTrue(encoder.convert(**kyargs) == 
                            {'Article': {'Type': {'href': 'ArticleType/2', 'Id': '2'}, 'Id': '1', 'Name': 'Article 1'}})
            
            kyargs['objInclude'] = ['Id']
            self.assertTrue(encoder.convert(**kyargs) == {'Article': {'Id': '1'}})
            
            del kyargs['objInclude']
            kyargs['objExclude'] = ['Type']
            self.assertTrue(encoder.convert(**kyargs) == {'Article': {'Id': '1', 'Name': 'Article 1'}})

            kyargs = dict(vtype=TypeModel(modelFor(ArticleType)), asString=asString, pathEncode=pathEncode)
            
            at = ArticleType()
            at.Id = 1
            at.Name = 'Article Type 1'
            kyargs['value'] = at
            kyargs['resourcePath'] = resourcesManager.findResourcePath(converterPath, ['ArticleType', '1'])
            
            self.assertTrue(encoder.convert(**kyargs) == 
                    {'ArticleType': {'Article': {'href': 'ArticleType/1/Article'}, 'Id': '1', 'Name': 'Article Type 1'}})

            # Test list paths convert
            kyargs = dict(vtype=Iter(TypeClass(Path, False)), asString=asString, pathEncode=pathEncode)
            kyargs['value'] = resourcesManager.findGetAllAccessible()
            
            self.assertTrue(encoder.convert(**kyargs) == 
                            {'Resources': {'Article': {'href': 'Article'}, 'ArticleType': {'href': 'ArticleType'}}})
            
            # Test list property convert
            kyargs = dict(vtype=Iter(Article.Id), asString=asString, pathEncode=pathEncode)
            kyargs['value'] = [1, 2]
            kyargs['resourcePath'] = resourcesManager.findResourcePath(converterPath, ['Article'])
            
            self.assertTrue(encoder.convert(**kyargs) == 
                            {'Article': [{'href': 'Article/1', 'Id': '1'}, {'href': 'Article/2', 'Id': '2'}]})
            
            kyargs['value'] = ['The Hulk 1', 'The Hulk 2']
            kyargs['vtype'] = Iter(Article.Name)
            self.assertTrue(encoder.convert(**kyargs) == 
                            {'Article': [{'Name': 'The Hulk 1'}, {'Name': 'The Hulk 2'}]})
            
            # Test list models convert
            kyargs = dict(vtype=Iter(Article), asString=asString, pathEncode=pathEncode)
            
            a1 = Article()
            a1.Id = 1
            a1.Name = 'Article 1'
            a1.Type = 1
            
            a2 = Article()
            a2.Id = 2
            a2.Name = 'Article 2'
            a2.Type = 2
            
            kyargs['value'] = (a1, a2)
            kyargs['resourcePath'] = resourcesManager.findResourcePath(converterPath, ['Article'])
            
            self.assertTrue(encoder.convert(**kyargs) == 
                            {'Article': [{'href': 'Article/1'}, {'href': 'Article/2'}]})
            
            kyargs['objInclude'] = ['Id']
            self.assertTrue(encoder.convert(**kyargs) == 
                            {'Article': [{'href': 'Article/1', 'Id': '1'}, {'href': 'Article/2', 'Id': '2'}]})
            
            kyargs['objInclude'] = ['Id', 'Type']
            self.assertTrue(encoder.convert(**kyargs) == 
            {'Article': [
                {'Type': {'href': 'ArticleType/1', 'Id': '1'}, 'Id': {'href': 'Article/1', 'Id': '1'}},
                {'Type': {'href': 'ArticleType/2', 'Id': '2'}, 'Id': {'href': 'Article/2', 'Id': '2'}}]})
            
            kyargs['objInclude'] = ['Id', 'Name']
            self.assertTrue(encoder.convert(**kyargs) == 
            {'Article': [{'Id': {'href': 'Article/1', 'Id': '1'}, 'Name': 'Article 1'},
                         {'Id': {'href': 'Article/2', 'Id': '2'}, 'Name': 'Article 2'}]})

        finally: ioc.close()
        
# --------------------------------------------------------------------
  
if __name__ == '__main__':
    unittest.main()
