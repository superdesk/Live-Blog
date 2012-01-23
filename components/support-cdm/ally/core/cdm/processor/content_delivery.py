'''
Created on Jul 14, 2011

@package: Newscoop
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides the content delivery handler.
'''

from ally.api.operator import GET, INSERT, UPDATE, DELETE
from ally.container.ioc import injected
from ally.core.spec.codes import METHOD_NOT_AVAILABLE
from ally.core.spec.resources import Path, Node
from ally.core.spec.server import Processor, Response, ProcessorsChain
from ally.core.http.spec import RequestHTTP
from os.path import isdir, isfile, join, dirname
import os
from zipfile import ZipFile, is_zipfile

# --------------------------------------------------------------------

@injected
class ContentDeliveryHandler(Processor):
    '''
    Implementation for a processor that delivers the content based on the URL.
    
    Provides on request: NA
    Provides on response: NA
    
    Requires on request: method, resourcePath
    Requires on response: NA

    @ivar documentRoot: string
        The HTTP server document root directory path
    @ivar repositorySubdir: string
        The sub - directory of the document root where the file repository is

    @see Processor
    '''

    documentRoot = str
    # The HTTP server document root directory path

    repositorySubdir = str
    # The sub-directory of the document root where the file repository is

    def __init__(self):
        assert isinstance(self.documentRoot, str) and isdir(self.documentRoot), \
            'Invalid document root directory %s' % self.documentRoot
        assert isinstance(self.repositorySubdir, str), \
            'Invalid repository sub-directory value %s' % self.documentRoot
        assert isdir(self.getRepositoryPath()) \
            and os.access(self.getRepositoryPath(), os.W_OK), \
            'Unable to access the repository directory %s' % self.documentRoot

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        path = req.resourcePath
        assert isinstance(path, Path)
        node = path.node
        assert isinstance(node, Node), \
        'The node has to be available in the path %s problems in previous processors' % path
        path = req.resourcePath
        assert isinstance(path, str)
        if req.method == INSERT: # Inserting
            self._sendNotAvailable(node, rsp, 'Path not available for post')
            return
        elif req.method == UPDATE: # Updating
            self._sendNotAvailable(node, rsp, 'Path not available for put')
            return
        elif req.method == DELETE: # Deleting
            self._sendNotAvailable(node, rsp, 'Path not available for delete')
            return
        elif req.method != GET:
            self._sendNotAvailable(node, rsp, 'Path not available for this method')
            return

        entryPath = join(self.documentRoot, self.repositorySubdir, req.path)
        writer = rsp.dispatch()
        if (isfile(entryPath)):
            try:
                f = open(entryPath)
                writer.write(f.read())
            except:
                rsp.code = 404
                return
        elif isfile(entryPath + '.link'):
            try:
                f = open(entryPath + '.link')
                linkedFilePath = f.readline().strip()
                lf = open(linkedFilePath)
                writer.write(lf.read())
            except:
                rsp.code = 404
                return
        else:
            linkPath = entryPath
            while len(linkPath) > 0:
                if is_zipfile(linkPath + '.ziplink'):
                    break
                linkPath = dirname(linkPath)
            else:
                rsp.code = 404
                return
            try:
                f = open(linkPath + '.ziplink')
                zipFilePath = f.readline().strip()
                inFilePath = f.readline().strip()
                zipFile = ZipFile(zipFilePath)
                file = zipFile.open(join(inFilePath, req.path))
                writer.write(file.read())
            except:
                rsp.code = 404
                return

        chain.process(req, rsp)

    def _sendNotAvailable(self, node, rsp, message):
        rsp.addAllows(GET)
        rsp.setCode(METHOD_NOT_AVAILABLE, message)
