'''
Created on August 19, 2013

@package: livedesk-sync
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Content for icons of collaborators of chained blogs.
'''

import socket
import logging
from urllib.request import urlopen
from ally.api.model import Content
from urllib.error import HTTPError
from ally.exception import InputError, Ref
from ally.internationalization import _

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class ChainedIconContent(Content):
    '''
    Simple remote icon content taking
    '''
    __slots__ = ('_url', '_response')

    def __init__(self, contentURL, fileName):
        '''
        Initialize the content.

        @param contentURL: string
            The URL of the icon to be downloaded.
        @param fileName: string
            The name of file under that the icon should be saved.
        '''
        Content.__init__(self, fileName, 'image', 'binary', 0)

        self._url = contentURL
        self._response = None

    def read(self, nbytes=None):
        '''
        @see: Content.read
        '''
        if not self._response:
            try: self._response = urlopen(self._url)
            except (HTTPError, socket.error) as e:
                log.error('Can not read icon image data %s' % e)
                raise InputError(Ref(_('Can not open icon URL'),))
            if not self._response:
                log.error('Can not read icon image data %s' % e)
                raise InputError(Ref(_('Can not open icon URL'),))
            if str(self._response.status) != '200':
                raise InputError(Ref(_('Can not open icon URL'),))

            self.type = self._response.getheader('Content-Type')
            if not self.type:
                self.type = 'image'
            self.length = self._response.getheader('Content-Length')
            if not self.length:
                self.length = 0

        if (not self._response) or self._response.closed:
            return ''

        try:
            if nbytes:
                return self._response.read(nbytes)
            return self._response.read()
        except (HTTPError, socket.error) as e:
            log.error('Can not read icon image data %s' % e)
            raise InputError(Ref(_('Can not read from icon URL'),))

    def next(self):
        '''
        @see: Content.next
        '''
        return None
