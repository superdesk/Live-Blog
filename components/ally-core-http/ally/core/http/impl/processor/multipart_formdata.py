'''
Created on Apr 24, 2012

package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the multipart form-data conversion to url encoded content.
'''

from .decoder_multipart import DecodingMultiPartHandler, ContentMultipart
from ally.container.ioc import injected
from ally.exception import DevelError
from io import BytesIO
from urllib.parse import urlencode
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class DecodingFormDataHandler(DecodingMultiPartHandler):
    '''
    Provides the multipart form data content handler processor.
    
    @see: DecodingMultiPartHandler
    
    Provides on request: req.content, req.content.contentType, req.content.contentTypeAttributes,
                         req.content.contentDisposition, req.content.contentDispositionAttributes
    Provides on response: NA
    
    Requires on request: req.content, req.content.contentType, req.content.contentTypeAttributes
    Requires on response: NA
    '''

    regexMultipart = '^multipart/form\-data$'
    # The regex for the content type value that dictates that the content is multipart form data.

    contentTypeUrlEncoded = str
    # The content type to set on the URL encoded form data.
    contentDisposition = 'form-data'
    # The content disposition for the form data.
    attrContentDispositionName = 'name'
    # The content disposition name.
    attrContentDispositionFile = 'filename'
    # The content disposition name.

    def __init__(self):
        super().__init__()
        assert isinstance(self.contentTypeUrlEncoded, str), \
        'Invalid content type URL encoded %s' % self.contentTypeUrlEncoded
        assert isinstance(self.contentDisposition, str), 'Invalid content disposition %s' % self.contentDisposition
        assert isinstance(self.attrContentDispositionName, str), \
        'Invalid content disposition name attribute %s' % self.attrContentDispositionName
        assert isinstance(self.attrContentDispositionFile, str), \
        'Invalid content disposition file attribute %s' % self.attrContentDispositionFile

    def _createContentMultipart(self, content, boundary):
        '''
        Provides additional form data.
        @see: DecodingMultiPartHandler._createContentMultipart
        '''
        content = super()._createContentMultipart(content, boundary)
        assert isinstance(content, ContentMultipart), 'Invalid multipart content %s' % content

        heritage = content.contentLanguage, content.contentConverter, content.objFormat
        parameters = []
        while True:
            if content.contentDisposition != self.contentDisposition:
                raise DevelError('Invalid multipart form data content disposition \'%s\'' % content.contentDisposition)
            if self.attrContentDispositionFile in content.contentDispositionAttributes:
                content = ContentFormDataFile(self, content)
                break

            name = content.contentDispositionAttributes.get(self.attrContentDispositionName)
            if not name: raise DevelError('No name in content disposition')

            value = str(content.read(), content.charSet)
            parameters.append((name, value))

            content = content.next()
            if not content: break

        if parameters:
            cnt = BytesIO(urlencode(parameters).encode(self.charSet, 'replace'))
            content = ContentFormDataUrlEncoded(cnt, content, *heritage)
            content.contentType = self.contentTypeUrlEncoded
            content.charSet = self.charSet

        return content

# --------------------------------------------------------------------

class ContentFormDataUrlEncoded(ContentDelegate, ContentRequestHTTP):
    '''
    Provides the form data URL encoded content.
    '''

    def __init__(self, content, nextContent, contentLanguage, contentConverter, objFormat):
        '''
        Constructs the form data content instance.
        
        @see: ContentDelegate.__init__
        
        @param nextContent: ContentRequest|None
            The content considered to be next to this content.
        '''
        assert nextContent is None or isinstance(nextContent, ContentRequest), 'Invalid next content %s' % nextContent
        ContentDelegate.__init__(self, content)
        ContentRequestHTTP.__init__(self)
        self.contentLanguage = contentLanguage
        self.contentConverter = contentConverter
        self.objFormat.update(objFormat)

        self._nextContent = nextContent

    def next(self):
        '''
        @see: ContentRequestHTTP.next
        '''
        return self._nextContent

class ContentFormDataFile(ContentDelegate, ContentRequestHTTP):
    '''
    Provides the form data content.
    '''

    def __init__(self, handler, content):
        '''
        Constructs the form data content instance.
        
        @see: ContentRequest.__init__
        
        @param handler: DecodingFormDataHandler
            The handler from where the form data content originated.
        @param content: ContentMultipart
            The form data multipart content.
        '''
        assert isinstance(handler, DecodingFormDataHandler), 'Invalid handler %s' % handler
        assert isinstance(content, ContentMultipart), 'Invalid multipart content %s' % content
        ContentDelegate.__init__(self, content)
        ContentRequestHTTP.__init__(self)

        self.contentLanguage = content.contentLanguage
        self.contentConverter = content.contentConverter
        self.objFormat.update(content.objFormat)
        self.name = None

        self._handler = handler

        self._processDispositions()

    def getName(self):
        '''
        @see: ContentRequest.getName
        '''
        return self.name

    def next(self):
        '''
        @see: ContentRequestHTTP.next
        '''
        self._content = self._content.next()
        if self._content:
            self._processDispositions()
            return self

    # ----------------------------------------------------------------

    def _processDispositions(self):
        '''
        Processes the multipart content dispositions to actual form data.
        '''
        content = self._content
        assert isinstance(content, ContentMultipart)
        self.name = content.contentDispositionAttributes.get(self._handler.attrContentDispositionFile)
        if not self.name: raise DevelError('A file upload can only have other file uploads following it, '
                                           'missing file name in content disposition')
        self.contentType = content.contentType
        self.charSet = content.charSet
