'''
Created on December 20, 2012

@package: url info
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API implementation for URL info service.
'''

from url_info.api.url_info import IURLInfoService, URLInfo
from urllib.request import urlopen, Request
from html.parser import HTMLParser, HTMLParseError
from datetime import datetime
from inspect import isclass
from ally.container.support import setup
from urllib.parse import unquote, urljoin
from urllib.error import URLError
from ally.exception import InputError

# --------------------------------------------------------------------

@setup(IURLInfoService, name='urlInfoService')
class URLInfoService(IURLInfoService):
    '''
    @see IURLInfoService
    '''

    def getURLInfo(self, url=None):
        '''
        @see: IURLInfoService.getURLInfo
        '''
        if not url: raise InputError('Invalid URL %s' % url)
        assert isinstance(url, str), 'Invalid URL %s' % url
        url = unquote(url)

        try:
            with urlopen(url) as conn:
                urlInfo = URLInfo()
                urlInfo.URL = url
                urlInfo.Date = datetime.now()
                contentType = None
                charset = 'utf_8'
                for tag, val in conn.info().items():
                    if tag == 'Content-Type':
                        contentTypeInfo = val.split(';')
                        contentType = contentTypeInfo[0].strip().lower();
                        if 2 == len(contentTypeInfo):
                            charset = contentTypeInfo[1].split('=')[1]
                        break
                if not contentType or contentType != 'text/html':
                    req = Request(url)
                    selector = req.get_selector().strip('/')
                    if selector:
                        parts = selector.split('/')
                        if parts: urlInfo.Title = parts[len(parts) - 1]
                    else:
                        urlInfo.Title = req.get_host()
                    return urlInfo
                elif contentType == 'text/html': urlInfo.ContentType = contentType
                extr = HTMLInfoExtractor(urlInfo)
                try:
                    readData = conn.read()
                    decodedData = ''
                    try:
                        decodedData = readData.decode(charset, 'ignore')
                    except Exception as e:
                        decodedData = readData.decode('utf_8', 'ignore')
                    repairPairs = [['<DOCTYPE html PUBLIC "-//W3C//DTD XHTML', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML']]
                    for onePair in repairPairs:
                        decodedData = decodedData.replace(onePair[0], onePair[1])
                    extr.feed(decodedData)
                except (AssertionError, HTMLParseError, UnicodeDecodeError): pass
                return extr.urlInfo
        except (URLError, ValueError): raise InputError('Invalid URL %s' % url)

# --------------------------------------------------------------------

META, TITLE, LINK, IMG = 'meta', 'title', 'link', 'img'

class HTMLInfoExtractor(HTMLParser):
    '''
    Extracts information for a given URL into the URLInfo entity.
    '''
    maxPictures = 10
    # the maximum number of pictures URLs to gather

    def __init__(self, urlInfo):
        assert isinstance(urlInfo, URLInfo), 'Invalid URL info %s' % urlInfo
        self.urlInfo = urlInfo
        self.state = None
        self.states = {TITLE:'Title'}
        self.stack = []
        super().__init__()

    def handle_starttag(self, tag, attrs):
        '''
        @see HTMLParser.handle_starttag
        '''
        assert isinstance(tag, str)
        tag = tag.lower()
        if tag in self.states and self.state != tag:
            self.state = tag
            self.stack.append(self.state)
        attrs = { attr.lower():val for attr, val in attrs }
        if tag == META:
            if 'name' in attrs and attrs['name'].lower() == 'description':
                self.urlInfo.Description = attrs['content'].strip()
        elif tag == LINK:
            if 'rel' in attrs and attrs['rel'].lower() == 'shortcut icon':
                self.urlInfo.SiteIcon = self._fullURL(self.urlInfo.URL, attrs['href'])
        elif tag == IMG:
            if 'src' in attrs:
                if isinstance(self.urlInfo.Picture, list):
                    self.urlInfo.Picture.append(self._fullURL(self.urlInfo.URL, attrs['src']))
                else:
                    self.urlInfo.Picture = [self._fullURL(self.urlInfo.URL, attrs['src'])]
        if self._done(): self.reset()

    def handle_endtag(self, tag):
        '''
        @see HTMLParser.handle_endtag
        '''
        assert isinstance(tag, str)
        tag = tag.lower()
        if tag in self.states and self.state == tag:
            self.stack.pop()
            self.state = self.stack.pop() if self.stack else None
        if self._done(): self.reset()

    def handle_data(self, data):
        '''
        @see HTMLParser.handle_data
        '''
        if self.state in self.states and self.states[self.state]:
            setattr(self.urlInfo, self.states[self.state], data)
        if self._done(): self.reset()

    def _fullURL(self, base, relative):
        assert isinstance(base, str), 'Invalid URL %s' % base
        assert isinstance(relative, str), 'Invalid URL %s' % relative
        return urljoin(base, relative)

    def _done(self):
        '''
        Return true if all the info was gathered.
        '''
        return self.urlInfo.Title and not isclass(self.urlInfo.Title) \
            and self.urlInfo.Description and not isclass(self.urlInfo.Description) \
            and self.urlInfo.SiteIcon and not isclass(self.urlInfo.SiteIcon) \
            and self.urlInfo.Picture and not isclass(self.urlInfo.Picture) and len(self.urlInfo.Picture) == self.maxPictures
