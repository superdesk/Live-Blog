'''
Created on Nov 21, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for plain text content converter.
'''

from content.resource.core.spec import IConverter
from ally.container.support import setup
import io

# --------------------------------------------------------------------

@setup(IConverter, name='converterTextPlain')
class ConverterTextPlain(IConverter):
    '''
    Implementation of converter API for plain text
    '''
    
    def __init__(self):
        self._content = io.StringIO()
        self._formatting = io.StringIO()

    def convert(self, token):
        '''
        Implementation of @see IConverter.convert
        '''
        assert isinstance(token, str), 'Invalid token %s' % token
        # TODO: implement
    
    def getContent(self):
        '''
        Implementation of @see IConverter.getContent
        '''
        return self._content
    
    def getFormatting(self):
        '''
        Implementation of @see IConverter.getFormatting
        '''
        return self._formatting
