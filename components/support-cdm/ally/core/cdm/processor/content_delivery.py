'''
Created on Jul 14, 2011

@package: cdm
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides the content delivery handler.
'''

from ally.api.config import GET
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
from ally.zip.util_zip import normOSPath, normZipPath
import json

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

    _linkExt = '.link'

    _zipHeader = 'ZIP'

    _fsHeader = 'FS'

    _linkTypes = dict

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
        self._linkTypes = { self._fsHeader : self._processLink,
                           self._zipHeader : self._processZiplink }

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

        # Make sure the given path points inside the repository
        entryPath = normOSPath(join(self.repositoryPath, normZipPath(req.path)))
        if not entryPath.startswith(self.repositoryPath):
            return rsp.setCode(RESOURCE_NOT_FOUND, 'Out of repository path')

        # Initialize the read file handler with None value
        # This will be set upon successful file open
        rf = None
        if isfile(entryPath):
            rf = open(entryPath, 'rb')
        else:
            linkPath = entryPath
            while len(linkPath) > len(self.repositoryPath):
                if isfile(linkPath + self._linkExt):
                    with open(linkPath + self._linkExt) as f: links = json.load(f)
                    subPath = normOSPath(entryPath[len(linkPath):]).lstrip(sep)
                    for linkType, *data in links:
                        if linkType in self._linkTypes:
                            # make sure the subpath is normalized and uses the OS separator
                            if not self._isPathDeleted(join(linkPath, subPath)):
                                rf = self._linkTypes[linkType](subPath, *data)
                                if rf is not None: break
                    break
                subLinkPath = dirname(linkPath)
                if subLinkPath == linkPath:
                    break
                linkPath = subLinkPath

        if rf is None:
            rsp.setCode(RESOURCE_NOT_FOUND, 'Invalid content resource')
        else:
            rsp.setCode(RESOURCE_FOUND, 'Resource found')
            rsp.content = readGenerator(rf)

    # ----------------------------------------------------------------

    def _processLink(self, subPath, linkedFilePath):
        '''
        Reads a link description file and returns a file handler to
        the linked file.
        '''
        # make sure the file path uses the OS separator
        linkedFilePath = normOSPath(linkedFilePath)
        if isdir(linkedFilePath):
            resPath = join(linkedFilePath, subPath)
        elif not subPath:
            resPath = linkedFilePath
        else:
            return None
        if isfile(resPath):
            return open(resPath, 'rb')

    def _processZiplink(self, subPath, zipFilePath, inFilePath):
        '''
        Reads a link description file and returns a file handler to
        the linked file inside the ZIP archive.
        '''
        # make sure the ZIP file path uses the OS separator
        zipFilePath = normOSPath(zipFilePath)
        # convert the internal ZIP path to OS format in order to use standard path functions
        inFilePath = normOSPath(inFilePath)
        zipFile = ZipFile(zipFilePath)
        # resource internal ZIP path should be in ZIP format
        resPath = normZipPath(join(inFilePath, subPath))
        if resPath in zipFile.NameToInfo:
            return zipFile.open(resPath, 'r')

    def _isPathDeleted(self, path):
        '''
        Returns true if the given path was deleted or was part of a directory
        that was deleted.
        '''
        path = normpath(path)
        while len(path) > len(self.repositoryPath):
            if isfile(path + '.deleted'): return True
            subPath = dirname(path)
            if subPath == path: break
            path = subPath
        return False
