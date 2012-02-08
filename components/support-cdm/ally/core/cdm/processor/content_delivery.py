'''
Created on Jul 14, 2011

@package: cdm
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides the content delivery handler.
'''

from ally.api.operator import GET
from ally.container.ioc import injected
from ally.core.http.spec import RequestHTTP
from ally.core.spec.codes import METHOD_NOT_AVAILABLE, RESOURCE_FOUND, \
    RESOURCE_NOT_FOUND
from ally.core.spec.server import Processor, Response, ProcessorsChain
from ally.support.util_io import readGenerator
from os.path import isdir, isfile, join, dirname, normpath, sep
from zipfile import ZipFile
import logging
import os

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ContentDeliveryHandler(Processor):
    '''
    Implementation for a processor that delivers the content based on the URL.
    
    Provides on request: NA
    Provides on response: NA
    
    Requires on request: method, resourcePath
    Requires on response: NA

    @ivar repositoryPath: string
        The directory where the file repository is

    @see Processor
    '''

    repositoryPath = str
    # The directory where the file repository is

    def __init__(self):
        assert isinstance(self.repositoryPath, str), \
            'Invalid repository path value %s' % self.repositoryPath
        self.repositoryPath = normpath(self.repositoryPath)
        if not os.path.exists(self.repositoryPath): os.makedirs(self.repositoryPath)
        assert isdir(self.repositoryPath) and os.access(self.repositoryPath, os.R_OK), \
            'Unable to access the repository directory %s' % self.repositoryPath
        super().__init__()

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        
        if req.method != GET:
            rsp.addAllows(GET)
            return rsp.setCode(METHOD_NOT_AVAILABLE, 'Path not available for method')
        
        entryPath = normpath(join(self.repositoryPath, req.path.replace('/', sep)))
        if not entryPath.startswith(self.repositoryPath):
            return rsp.setCode(RESOURCE_NOT_FOUND, 'Out of repository path')
        
        if isfile(entryPath): rf = open(entryPath, 'rb')
        else:
            linkPath = entryPath
            while len(linkPath) > len(self.repositoryPath):
                if isfile(linkPath + '.link'):
                    rf = self._processLink(linkPath, entryPath[len(linkPath):])
                    break
                if isfile(linkPath + '.ziplink'):
                    rf = self._processZiplink(linkPath, entryPath[len(linkPath):])
                    break
                subLinkPath = dirname(linkPath)
                if subLinkPath == linkPath:
                    rf = None
                    break
                linkPath = subLinkPath
            else: rf = None
            
        if rf is None: rsp.setCode(RESOURCE_NOT_FOUND, 'Invalid content resource')
        else:
            rsp.setCode(RESOURCE_FOUND, 'Resource found')
            rsp.content = readGenerator(rf)

    # ----------------------------------------------------------------
    
    def _processLink(self, linkPath, subPath):
        subPath = subPath.lstrip(sep)
        with open(linkPath + '.link') as f:
            linkedFilePath = f.readline().strip()
            if isdir(linkedFilePath):
                resPath = join(linkedFilePath, subPath)
            elif not subPath:
                resPath = linkedFilePath
            if not self._isPathDeleted(join(linkPath, subPath)) and isfile(resPath):
                return open(resPath, 'rb')

    def _processZiplink(self, linkPath, subPath):
        subPath = subPath.lstrip(sep)
        with open(linkPath + '.ziplink') as f:
            zipFilePath = f.readline().strip()
            inFilePath = f.readline().strip()
            zipFile = ZipFile(zipFilePath)
            resPath = join(inFilePath, subPath)
            if not self._isPathDeleted(join(linkPath, subPath)) and resPath in zipFile.filelist:
                return zipFile.open(resPath, 'r')

    def _isPathDeleted(self, path):
        path = normpath(path)
        while len(path) > len(self.repositoryPath):
            if isfile(path + '.deleted'): return True
            subPath = dirname(path)
            if subPath == path: break
            path = subPath
        return False

# --------------------------------------------------------------------
