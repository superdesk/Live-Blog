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
from ally.core.spec.codes import METHOD_NOT_AVAILABLE, RESOURCE_FOUND, RESOURCE_NOT_FOUND
from ally.core.spec.server import Processor, Response, ProcessorsChain
from ally.core.http.spec import RequestHTTP
from os.path import isdir, isfile, join, dirname
import os
from zipfile import ZipFile
from ally.support.util_io import pipe

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
        assert isdir(self.repositoryPath) \
            and os.access(self.repositoryPath, os.R_OK), \
            'Unable to access the repository directory %s' % self.repositoryPath
        super().__init__()

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if req.method == INSERT: # Inserting
            self._sendNotAvailable(rsp, 'Path not available for post')
            return
        elif req.method == UPDATE: # Updating
            self._sendNotAvailable(rsp, 'Path not available for put')
            return
        elif req.method == DELETE: # Deleting
            self._sendNotAvailable(rsp, 'Path not available for delete')
            return
        elif req.method != GET:
            self._sendNotAvailable(rsp, 'Path not available for this method')
            return

        entryPath = join(self.repositoryPath, req.path)
        rsp.setCode(RESOURCE_FOUND, 'File found')
        if (isfile(entryPath)):
            try:
                with open(entryPath, 'rb') as f:
                    pipe(f, rsp.dispatch())
            except:
                return rsp.setCode(RESOURCE_NOT_FOUND, 'Unable to read resource file')
        else:
            linkPath = entryPath
            try:
                while len(linkPath.lstrip('/')) > 0:
                    subPath = entryPath[len(linkPath):].lstrip('/')
                    if isfile(linkPath + '.link'):
                        rf = self._processLink(linkPath, subPath)
                        break
                    if isfile(linkPath + '.ziplink'):
                        rf = self._processZiplink(linkPath, subPath)
                        break
                    linkPath = dirname(linkPath)
                else:
                    return rsp.setCode(RESOURCE_NOT_FOUND, 'Invalid resource')
                pipe(rf, rsp.dispatch())
                rf.close()
            except Exception as e:
                return rsp.setCode(RESOURCE_NOT_FOUND, str(e))

        chain.proceed()

    def _processLink(self, linkPath, subPath):
        with open(linkPath + '.link') as f:
            linkedFilePath = f.readline().strip()
            if isdir(linkedFilePath):
                resPath = join(linkedFilePath, subPath.lstrip('/'))
            elif len(subPath) > 0:
                raise Exception('Invalid link to a file in file')
            else:
                resPath = linkedFilePath
            if self._isPathDeleted(join(linkPath, subPath)):
                raise Exception('Resource was deleted')
            return open(resPath, 'rb')

    def _processZiplink(self, linkPath, subPath):
        with open(linkPath + '.ziplink') as f:
            zipFilePath = f.readline().strip()
            inFilePath = f.readline().strip()
            zipFile = ZipFile(zipFilePath)
            if self._isPathDeleted(join(linkPath, subPath)):
                raise Exception('Resource was deleted')
            return zipFile.open(join(inFilePath, subPath), 'r')

    def _sendNotAvailable(self, rsp, message):
        rsp.addAllows(GET)
        rsp.setCode(METHOD_NOT_AVAILABLE, message)

    def _isPathDeleted(self, path):
        if isfile(path + '.deleted'):
            return True
        subPath = dirname(path)
        while len(subPath.strip('/')) > 0:
            if isfile(subPath + '.deleted'):
                return True
            subPath = dirname(subPath)
        return False
