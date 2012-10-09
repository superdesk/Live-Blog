'''
Created on Aug 28, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the text parser processor handler.
'''

from .base import ParseBaseHandler
from ally.container.ioc import injected
from ally.support.util_io import IInputStream
from collections import Callable, deque
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ParseTextHandler(ParseBaseHandler):
    '''
    Provides the text parsing.
    @see: ParseBaseHandler
    '''

    parser = Callable
    # A Callable(file, string) function used for decoding a bytes file to a text object.
    parserName = str
    # The parser

    def __init__(self):
        assert callable(self.parser), 'Invalid callable parser %s' % self.parser
        assert isinstance(self.parserName, str), 'Invalid parser name %s' % self.parserName
        super().__init__()

        self.contentType = next(iter(self.contentTypes))

    def parse(self, decoder, data, source, charSet):
        '''
        @see: ParseBaseHandler.parse
        '''
        assert callable(decoder), 'Invalid decoder %s' % decoder
        assert isinstance(data, dict), 'Invalid data %s' % data
        assert isinstance(source, IInputStream), 'Invalid stream %s' % source
        assert isinstance(charSet, str), 'Invalid character set %s' % charSet

        try: obj = self.parser(source, charSet)
        except ValueError: return 'Bad %s content' % self.parserName

        process = deque()
        process.append((deque(), obj))
        while process:
            path, obj = process.popleft()
            if obj is None or isinstance(obj, (str, list)):
                if not decoder(path=deque(path), value=obj, **data): return 'Invalid path \'%s\' in object' % '/'.join(path)

            elif isinstance(obj, dict):
                for name, value in obj.items():
                    itemPath = deque(path)
                    itemPath.append(name)
                    process.append((itemPath, value))
