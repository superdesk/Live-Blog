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
from ally.api.type import TypeModel, Iter, TypeClass
from ally.container import ioc, aop
from ally.core.impl.processor.encdec_text import EncodingTextHandler
import unittest
from ally.core.spec.resources import ResourcesManager, Path

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
            
            # Test path convert
            kyargs = dict(vtype=Iter(TypeClass(Path, False)), asString=asString, pathEncode=pathEncode)
            kyargs['value'] = resourcesManager.findGetAllAccessible()
            
            self.assertTrue(encoder.convert(**kyargs) == 
                            {'Resources': {'Article': {'href': 'Article'}, 'ArticleType': {'href': 'ArticleType'}}})
            
            # Test model convert
            kyargs = dict(vtype=TypeModel(modelFor(Article)), asString=asString, pathEncode=pathEncode)
            
            a = Article()
            a.Id = 1
            a.Name = 'Article 1'
            a.Type = 2
            kyargs['value'] = a
            kyargs['resourcePath'] = resourcesManager.findResourcePath(converterPath, ['Article', '1'])
            
            self.assertTrue(encoder.convert(**kyargs) == 
                            {'Article': {'Type': {'href': 'ArticleType/2', 'Type': '2'}, 'Id': '1', 'Name': 'Article 1'}})
            
            kyargs['objInclude'] = ['Id']
            self.assertTrue(encoder.convert(**kyargs) == {'Article': {'Id': '1'}})
            
            del kyargs['objInclude']
            kyargs['objExclude'] = ['Type']
            self.assertTrue(encoder.convert(**kyargs) == {'Article': {'Id': '1', 'Name': 'Article 1'}})
            
        finally: ioc.close()
        
# --------------------------------------------------------------------
  
if __name__ == '__main__':
    unittest.main()
