'''
Created on Jan 26, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the encoder and decoder xml.
'''

import unittest
from ally.core.impl.processor.encdec_text_support.encoder_xml import XMLEncoder
from ally.container import ioc
from io import StringIO

# --------------------------------------------------------------------

class TestEncDecXML(unittest.TestCase):
        
    def testEncoderXML(self):
        encoder = XMLEncoder()
        ioc.initialize(encoder)
        
        # Test Property encoding
        out = StringIO()
        encoder.encode({'href': 'Article/1', 'Id': '1'}, out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<Id href="Article/1">1</Id>''')
        
        out = StringIO()
        encoder.encode({'Name': 'The Name'}, out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<Name>The Name</Name>''')
        
        # Test Model encoding
        out = StringIO()
        encoder.encode({'Article': {'Type': {'href': 'ArticleType/2', 'Id': '2'}, 'Id': '1', 'Name': 'Article 1'}}, 
                       out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<Article><Type href="ArticleType/2">2</Type><Id>1</Id><Name>Article 1</Name></Article>''')
        
        out = StringIO()
        encoder.encode({'Article': {'Id': '1'}},  out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<Article><Id>1</Id></Article>''')
        
        out = StringIO()
        encoder.encode({'Article': {'Id': '1', 'Name': 'Article 1'}},  out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<Article><Id>1</Id><Name>Article 1</Name></Article>''')
        
        out = StringIO()
        encoder.encode({'Article': {'Id': '1', 'Name': 'Article 1'}},  out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<Article><Id>1</Id><Name>Article 1</Name></Article>''')
        
        out = StringIO()
        encoder.encode({'ArticleType': {'Article': {'href': 'ArticleType/1/Article'}, 'Id': '1', 
                                        'Name': 'Article Type 1'}},  out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleType><Article href="ArticleType/1/Article"/><Id>1</Id><Name>Article Type 1</Name></ArticleType>''')
        
        # Test list paths encoding
        out = StringIO()
        encoder.encode({'Resources': {'Article': {'href': 'Article'}, 'ArticleType': {'href': 'ArticleType'}}}, 
                       out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<Resources><Article href="Article"/><ArticleType href="ArticleType"/></Resources>''')
        
        # Test list property encoding
        out = StringIO()
        encoder.encode({'Article': [{'href': 'Article/1', 'Id': '1'}, {'href': 'Article/2', 'Id': '2'}]}, 
                       out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList><Id href="Article/1">1</Id><Id href="Article/2">2</Id></ArticleList>''')
        
        out = StringIO()
        encoder.encode({'Article': [{'Name': 'The Hulk 1'}, {'Name': 'The Hulk 2'}]}, 
                       out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList><Name>The Hulk 1</Name><Name>The Hulk 2</Name></ArticleList>''')
        
        # Test list models convert
        out = StringIO()
        encoder.encode({'Article': [{'href': 'Article/1'}, {'href': 'Article/2'}]}, 
                       out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList><Article href="Article/1"/><Article href="Article/2"/></ArticleList>''')
        
        out = StringIO()
        encoder.encode({'Article': [{'href': 'Article/1', 'Id': '1'}, {'href': 'Article/2', 'Id': '2'}]}, 
                       out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList><Id href="Article/1">1</Id><Id href="Article/2">2</Id></ArticleList>''')
        
        out = StringIO()
        encoder.encode(
        {'Article': [
                {'Type': {'href': 'ArticleType/1', 'Id': '1'}, 'Id': {'href': 'Article/1', 'Id': '1'}},
                {'Type': {'href': 'ArticleType/2', 'Id': '2'}, 'Id': {'href': 'Article/2', 'Id': '2'}}]}, 
                       out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList><Article><Type href="ArticleType/1">1</Type><Id href="Article/1">1</Id></Article>'''\
'<Article><Type href="ArticleType/2">2</Type><Id href="Article/2">2</Id></Article></ArticleList>')
        
        out = StringIO()
        encoder.encode({'Article': [{'Id': {'href': 'Article/1', 'Id': '1'}, 'Name': 'Article 1'},
                                    {'Id': {'href': 'Article/2', 'Id': '2'}, 'Name': 'Article 2'}]}, 
                       out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList><Article><Id href="Article/1">1</Id><Name>Article 1</Name></Article>'''\
'<Article><Id href="Article/2">2</Id><Name>Article 2</Name></Article></ArticleList>')
        
        out = StringIO()
        encoder.encode(
        {'Article': [
            {'Type': {'href': 'ArticleType/1', 'Id': '1', 'Name': 'Type 1'}, 'Id': {'href': 'Article/1', 'Id': '1'}},
            {'Type': {'href': 'ArticleType/2', 'Id': '2', 'Name': 'Type 2'}, 'Id': {'href': 'Article/2', 'Id': '2'}}]}, 
                       out, 'UTF-8')
        self.assertTrue(out.getvalue() == 
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList>'''\
'<Article><Type href="ArticleType/1"><Id>1</Id><Name>Type 1</Name></Type><Id href="Article/1">1</Id></Article>'\
'<Article><Type href="ArticleType/2"><Id>2</Id><Name>Type 2</Name></Type><Id href="Article/2">2</Id></Article>'\
'</ArticleList>')
    
# --------------------------------------------------------------------
  
if __name__ == '__main__':
    unittest.main()
