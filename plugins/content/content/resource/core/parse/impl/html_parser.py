'''
Created on Dec 2, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides an HTML parser.
'''

from html.parser import HTMLParser, HTMLParseError
from ally.support.util_io import IInputStream, IOutputStream

# --------------------------------------------------------------------

TAGS_MAP = dict(html='html', head='head', body='body', h1='header1', h2='header2', h3='header3',
                h4='header4', h5='header5', h6='header6', ul='ul', ol='ol', li='li', b='bold',
                br='br', div='div', p='paragraph', small='small', strong='strong', style='style',
                sub='sub', sup='sup', u='underline')

BLOCK_TAGS = ('html', 'head', 'body', 'ul', 'ol', 'li', 'b', 'div', 'p', 'small', 'strong', 'style',
              'sub', 'sup', 'u')

START_SYMBOL = 'start'
END_SYMBOL = 'end'
START_END_SYMBOL = 'start-end'

class TextItemHMTLParser(HTMLParser):
    '''
    Parser used to extract HTML tags and generate separate plain text
    and content formatting from the original HTML content.
    '''
    
    def __init__(self, strict=False, acceptUnknownTags=False):
        '''
        @param strict: boolean
            If strict is set to True (the default), errors are raised when invalid
            HTML is encountered.  If set to False, an attempt is instead made to
            continue parsing, making "best guesses" about the intended meaning, in
            a fashion similar to what browsers typically do.
        @param acceptUnknownTags: boolean
            If True will allow unknown tags if False will throw exception when encountering an
            unknown tag.
        '''
        assert isinstance(strict, bool), 'Invalid strict flag %s' % strict
        assert isinstance(acceptUnknownTags, bool), 'Invalid accept unknown tags flag %s' % acceptUnknownTags

        super().__init__(strict=strict)
        self.acceptUnknownTags = acceptUnknownTags

    def parse(self, inp, charSet, out):
        '''
        Parse an input stream
        
        @param inp: IInputStream
            The input stream
        @param charSet: str
            The input stream character set
        @param out: IInputStream
            The output stream
        '''
        assert isinstance(inp, IInputStream), 'Invalid input stream %s' % inp
        assert isinstance(charSet, str), 'Invalid character set %s' % charSet
        assert isinstance(inp, IOutputStream), 'Invalid output stream %s' % out
        
        self._out = out
        self._format = dict()
        self._pos = 0
        self._tagsStack = []
        buf = inp.read(1000)
        while buf:
            self.feed(buf.decode(charSet if charSet else 'utf-8'))
            buf = inp.read(1000)
        return self._format

    def handle_starttag(self, tag, attrs):
        '''
        @see HTMLParser.handle_starttag
        '''
        assert isinstance(tag, str), 'Invalid tag %s' % tag
        tag = tag.lower()
        symbol = TAGS_MAP.get(tag)
        if not symbol and not self.acceptUnknownTags:
            raise HTMLParseError('Unsupported tag %s at line %s and column %s' % (tag, self.getpos()))
        if self._currentTag() and self._currentTag() not in BLOCK_TAGS:
            raise HTMLParseError('Invalid tag %s at line %s and column %s' % (tag, self.getpos()))
    
        self._format[self._pos] = '%s:%s' % (symbol, START_SYMBOL)
        if self._currentTag() != tag: self._tagsStack.append(tag)
        
    def handle_endtag(self, tag):
        '''
        @see HTMLParser.handle_endtag
        '''
        assert isinstance(tag, str), 'Invalid tag %s' % tag
        symbol = TAGS_MAP.get(tag.lower())
        if not symbol and not self.acceptUnknownTags:
            raise HTMLParseError('Unsupported tag %s at line %s and column %s' % (tag, self.getpos()))
        self._format[self._pos] = '%s:%s' % (symbol, END_SYMBOL)
        self._dropTagsSince(tag)

    def handle_startendtag(self, tag, attrs):
        '''
        @see HTMLParser.handle_startendtag
        '''
        assert isinstance(tag, str), 'Invalid tag %s' % tag
        symbol = TAGS_MAP.get(tag.lower())
        if not symbol and not self.acceptUnknownTags:
            raise HTMLParseError('Unsupported tag %s at line %s and column %s' % (tag, self.getpos()))
        self._format[self._pos] = '%s:%s' % (symbol, START_END_SYMBOL)

    def handle_data(self, data):
        '''
        @see HTMLParser.handle_data
        '''
        assert isinstance(data, str), 'Invalid text %s' % data
        if len(data) == 0: return
        self._out.write(data)
        self._pos += len(data)

    # ----------------------------------------------------------------

    def _currentTag(self):
        if self._tagsStack:
            return self._tagsStack[-1]
        return None

    def _dropTagsSince(self, tag):
        if not tag in self._tagsStack: return
        lastTag = self._tagsStack.pop()
        while lastTag != tag:
            lastTag = self._tagsStack.pop()
