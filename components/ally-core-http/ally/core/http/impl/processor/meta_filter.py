'''
Created on Feb 1, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the meta creation processor handler that also makes filtering on the meta based on the X-Filter header.
'''

from .header import HeaderHTTPBase, VALUES
from ally.api.config import GET
from ally.container.ioc import injected
from ally.core.http.spec import INVALID_HEADER_VALUE
from ally.core.impl.processor.meta_creator import MetaCreatorHandler, \
    sortProperties
from ally.core.spec.data_meta import MetaLink, MetaModel, MetaPath, \
    MetaCollection, MetaFetch
from ally.core.spec.resources import Normalizer
from ally.core.spec.server import Request, Response, ProcessorsChain, Processors
from ally.exception import DevelError
from collections import deque
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class MetaFilterHandler(MetaCreatorHandler, HeaderHTTPBase):
    '''
    Provides the meta filtering. 
    
    Provides on request: NA
    Provides on response: [objMeta]
    
    Requires on request: headers
    Requires on response: objMeta
    '''

    normalizer = Normalizer
    # The normalizer used for matching property names with header values.
    fetching = Processors
    # The processors used in fetching.
    nameXFilter = 'X-Filter'
    # The header name for the filter.
    separatorNames = '.'
    # Separator used for filter names.

    def __init__(self):
        MetaCreatorHandler.__init__(self)
        HeaderHTTPBase.__init__(self)
        assert isinstance(self.normalizer, Normalizer), 'Invalid Normalizer object %s' % self.normalizer
        assert isinstance(self.fetching, Processors), 'Invalid fetching processors %s' % self.fetching
        assert isinstance(self.nameXFilter, str), 'Invalid filter header name %s' % self.nameXFilter
        assert isinstance(self.separatorNames, str), 'Invalid names separator %s' % self.separatorNames

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, Request), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain

        try:
            filterBy = self._parse(self.nameXFilter, req.headers, req.params, VALUES)
        except DevelError as e:
            assert isinstance(e, DevelError)
            rsp.setCode(INVALID_HEADER_VALUE, e.message)
            return

        _hasFetcher = False

        if rsp.objMeta is None:
            if filterBy:
                rsp.setCode(INVALID_HEADER_VALUE, 'Unknown filter properties %r' % ', '.join(filterBy))
                return
        else:
            filterTree = {}
            while filterBy:
                names = filterBy.pop().split(self.separatorNames)
                fdict = filterTree
                for fname in names:
                    fvalue = fdict.get(fname)
                    if not isinstance(fvalue, dict): fvalue = fdict[fname] = {}
                    fdict = fvalue

            _hasFetcher = False
            def createFetcher(meta):
                nonlocal _hasFetcher
                _hasFetcher = True
                return Fetcher(self.fetching, req, rsp, meta)

            rsp.objMeta = self.filterMeta(rsp.objMeta, self.normalizer.normalize, createFetcher, filterTree, True)
            if filterTree:
                unknown, process = [], deque()
                process.append((filterTree, ''))
                while process:
                    fdict, name = process.pop()
                    for fname, fvalue in fdict.items():
                        if fvalue: process.append((fvalue, ''.join((name, fname, self.separatorNames))))
                        else: unknown.append(name + fname)

                rsp.setCode(INVALID_HEADER_VALUE, 'Unknown filter(s) %r' % ', '.join(unknown))
                return

        if _hasFetcher:
            chain.process(req, rsp)
            if rsp.code.isSuccess:
                # If there is a registered fetcher we need to bring the entire content because the fetching is lazy loading
                # so if there is any problem while fetching we need to be able to report that, so the content is fetched
                # before the rendering so in a case of a fetch problem we can abort.
                try:
                    content = [bytes for bytes in rsp.content]
                except FetchError: rsp.content = None
                else: rsp.content = iter(content)
        else: chain.proceed()

    # ----------------------------------------------------------------

    def filterMeta(self, meta, normalize, createFetcher, filterTree={}, first=False):
        '''
        Filters the provided meta based on the filter tree.
        
        @param meta: meta object
            The meta object to be filtered.
        @param normalize: callable
            The call used for normalize the names.
        @param createFetcher: callable
            The call used for creating fetcher based on a meta.
        @param filterTree: dictionary{string, dictionary{string, ...}}
            The filter tree for the meta, the filter tree is consumed whenever a valid filter is found. All the filters
            that have not been recognized will be left in the filter tree structure.
        @param first: boolean
            Flag indicating that this is the first meta entry, False otherwise.
        @return: meta object
            The filtered meta object.
        '''
        assert meta is not None, 'A meta object is required'
        assert callable(normalize), 'Invalid normalize %s' % normalize
        assert callable(createFetcher), 'Invalid create fetcher %s' % createFetcher
        assert isinstance(filterTree, dict), 'Invalid filter dictionary %s' % filterTree
        assert isinstance(first, bool), 'Invalid first flag %s' % first

        if isinstance(meta, MetaCollection):
            if isinstance(meta.metaItem, MetaModel):
                assert isinstance(meta, MetaCollection)
                return MetaCollection(self.filterMeta(meta.metaItem, normalize, createFetcher, filterTree),
                                      meta.getItems, meta.getTotal)

        elif isinstance(meta, MetaModel):
            assert isinstance(meta, MetaModel)
            if filterTree:
                metas, unknownNames = {}, set(filterTree)
                for name, pmeta in meta.properties.items():
                    nname = normalize(name)
                    f = filterTree.get(nname, None)
                    if f is not None:
                        if not f:
                            metas[name] = pmeta
                            del filterTree[nname]
                        else:
                            metas[name] = self.filterMeta(pmeta, normalize, createFetcher, f)
                            if not f: del filterTree[nname]
                        unknownNames.remove(nname)
                    elif first: metas[name] = pmeta

                if unknownNames and isinstance(meta.metaLink, MetaPath):
                    # If there are unknown filter names we will try to see if there are in the full meta model.
                    metaModel = self.meta(meta.model.type, meta.metaLink.path)
                    addAll = filterTree.get('*', None)
                    if addAll is not None:
                        if not addAll: del filterTree['*']
                        addAll = True
                    fmetas = {}
                    for name, pmeta in metaModel.properties.items():
                        nname = normalize(name)
                        if nname in unknownNames:
                            f = filterTree[nname]
                            # We wrap the meta in a fetch that will deliver as a value the second value from a pack.
                            if not f:
                                fmetas[name] = MetaFetch(pmeta, fetchSecond)
                                del filterTree[nname]
                            else:
                                fmetas[name] = MetaFetch(self.filterMeta(pmeta, normalize, createFetcher, f), fetchSecond)
                                if not f: del filterTree[nname]
                        elif addAll: fmetas[name] = MetaFetch(pmeta, fetchSecond)
                    if fmetas:
                        # If we found fetched metas from the full meta model we need to adjust the meta get values 
                        # functions in order to take the first value from a tuple of values the second value is taken
                        # by the full meta model metas.
                        metas = {name: MetaFetch(pmeta, fetchFirst) for name, pmeta in metas.items()}
                        # We can now join the original metas with the fetched metas.
                        metas.update(fmetas)
                        return MetaModel(meta.model, createFetcher(meta), meta.metaLink,
                                         sortProperties(meta.model, metas))

                return MetaModel(meta.model, meta.getModel, meta.metaLink, sortProperties(meta.model, metas))
            elif not first and meta.metaLink:
                return MetaModel(meta.model, meta.getModel, meta.metaLink)

        return meta

# --------------------------------------------------------------------

class FetchError(Exception):
    '''
    Exception raised when a fetch problem occurs.
    '''

fetchFirst = lambda pack: pack[0]
# Function used to fetch the first value from a fetcher return tuple
fetchSecond = lambda pack: pack[1]
# Function used to fetch the second value from a fetcher return tuple

class Fetcher:
    '''
    The fetcher provides the ability to get the additional models to be presented.
    '''

    __slots__ = ('processors', 'request', 'response', 'meta',)

    def __init__(self, processors, request, response, meta):
        '''
        Constructs the fetcher base on the meta model
        
        @param processors: Processors
            The processors used in fetching the data.
        @param request: Request
            The request to be processed.
        @param response: Response
            The response to be processed.
        @param meta: MetaModel
            The meta model that this fetcher wraps and extends.
        '''
        assert isinstance(processors, Processors), 'Invalid processors %s' % processors
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(meta, MetaModel), 'Invalid meta model %s' % meta
        assert isinstance(meta.metaLink, MetaLink), 'Invalid  meta model %s, has no meta link' % meta
        self.processors = processors
        self.request = request
        self.response = response
        self.meta = meta

    def __call__(self, obj):
        model = self.meta.getModel(obj)
        if model is None: return

        path = self.meta.metaLink.getLink(obj)
        if path is None: return (model, None)

        req = Request()
        req.method = GET
        req.resourcePath = path
        req.accLanguages = self.request.accLanguages
        req.params.extend(self.request.params)

        rsp = Response()
        rsp.contentLanguage = self.response.contentLanguage

        chain = self.processors.newChain()
        assert isinstance(chain, ProcessorsChain)
        chain.process(req, rsp)
        if rsp.code and not rsp.code.isSuccess:
            self.response.code = rsp.code
            self.response.codeText = rsp.codeText
            self.response.codeMessage = rsp.codeMessage
            raise FetchError()

        return model, rsp.obj
