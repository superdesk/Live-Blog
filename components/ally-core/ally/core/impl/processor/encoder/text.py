'''
Created on Jan 25, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text encoder processor handler that creates text objects to be encoded.
'''

from .text_base import EncoderTextBaseHandler
from ally.container.ioc import injected
from ally.core.spec.meta import Meta, Object, Value, Collection
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class EncoderTextHandler(EncoderTextBaseHandler):
    '''
    Provides the text object encoding.
    @see: EncodingTextBaseHandler
    '''

    encoder = None
    # A Callable(object, string) function used for creating the text generator object that takes as the first argument
    # the text object to be encoded, and on the last position the character set encoding to be used.

    def __init__(self):
        super().__init__()
        assert callable(self.encoder), 'Invalid callable encoder %s' % self.encoder

    def renderMeta(self, meta, charSet):
        '''
        @see: EncoderTextBaseHandler.renderMeta
        '''
        return self.encoder(self.convertMeta(meta), charSet)

    def convertMeta(self, meta):
        '''
        Convert the provided meta to a text object.
        
        @param meta: Meta
            The meta do convert.
        @return: dictionary
            The converted text object.
        '''
        assert isinstance(meta, Meta), 'Invalid meta %s' % meta

        if isinstance(meta, Object):
            assert isinstance(meta, Object)
            return {meta.identifier:{prop.identifier:self.convertMeta(prop) for prop in meta.properties}}

        if isinstance(meta, Collection):
            assert isinstance(meta, Collection)
            return {meta.identifier:[self.convertMeta(item) for item in meta.items]}

        assert isinstance(meta, Value), 'Unknown meta %s' % meta
        return meta.value
