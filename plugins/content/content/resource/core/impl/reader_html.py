'''
Created on Nov 21, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for HTML content reader.
'''

from content.resource.core.spec import IReader
from ally.api.model import Content
from ally.container.support import setup

# --------------------------------------------------------------------

@setup(IReader, name='readerHTML')
class ReaderHTML(IReader):
    '''
    Implementation of reader API for HTML content
    '''
    
    def register(self, readers):
        '''
        Implementation of @see IReader.parse
        '''
        assert isinstance(readers, dict), 'Invalid readers dictionary %s' % readers
        readers['text/html'] = ReaderHTML

    def parse(self, content):
        '''
        Implementation of @see IReader.parse
        '''
        assert isinstance(content, Content), 'Invalid content %s' % content
        # TODO: implement
