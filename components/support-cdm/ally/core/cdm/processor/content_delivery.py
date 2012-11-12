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
from ally.core.spec.codes import METHOD_NOT_AVAILABLE, RESOURCE_FOUND, \
    RESOURCE_NOT_FOUND, Code
from ally.design.context import Context, requires, defines
from ally.design.processor import Chain, Processor, Assembly, NO_VALIDATION, \
    Processing, Handler
from ally.support.util_io import IOutputStream
from ally.zip.util_zip import normOSPath, normZipPath
from functools import partial
from mimetypes import guess_type
from os.path import isdir, isfile, join, dirname, normpath, sep
from urllib.parse import unquote
from zipfile import ZipFile
import json
import logging
import os

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    scheme = requires(str)
    uri = requires(str)
    method = requires(int)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(Code, doc='''
    @rtype: Code
    The code of the response.
    ''')
    text = defines(str, doc='''
    @rtype: string
    A small text message for the code, usually placed in the response.
    ''')
    allows = defines(int, doc='''
    @rtype: integer
    Contains the allow flags for the methods.
    ''')
    length = defines(int, doc='''
    @rtype: integer
    Contains the length for the content.
    ''')

class ResponseContent(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    source = defines(IOutputStream, doc='''
    @rtype: IOutputStream
    The generator that provides the response content in bytes.
    ''')
    type = defines(str, doc='''
    @rtype: string
    The type for the streamed content.
    ''')

# --------------------------------------------------------------------

@injected
class ContentDeliveryHandler(Handler):
    '''
    Implementation for a processor that delivers the content based on the URL.
    '''

    repositoryPath = str
    # The directory where the file repository is
    defaultContentType = 'application/octet-stream'
    # The default mime type to set on the content response if None could be guessed
    _linkExt = '.link'
    # Extension to mark the link files in the repository.
    _zipHeader = 'ZIP'
    # Marker used in the link file to indicate that a link is inside a zip file.
    _fsHeader = 'FS'
    # Marker used in the link file to indicate that a link is file system
    errorAssembly = Assembly
    # The error processors, this are used when the content is not available.

    def __init__(self):
        assert isinstance(self.repositoryPath, str), 'Invalid repository path value %s' % self.repositoryPath
        assert isinstance(self.defaultContentType, str), 'Invalid default content type %s' % self.defaultContentType
        self.repositoryPath = normpath(self.repositoryPath)
        if not os.path.exists(self.repositoryPath): os.makedirs(self.repositoryPath)
        assert isdir(self.repositoryPath) and os.access(self.repositoryPath, os.R_OK), \
            'Unable to access the repository directory %s' % self.repositoryPath
        assert isinstance(self.errorAssembly, Assembly), 'Invalid error assembly %s' % self.errorAssembly
        errorProcessing = self.errorAssembly.create(NO_VALIDATION, request=Request, response=Response,
                                                    responseCnt=ResponseContent)
        assert isinstance(errorProcessing, Processing), 'Invalid processing %s' % errorProcessing

        super().__init__(Processor(errorProcessing.contexts, partial(self.process, errorProcessing),
                                   'process', self.process.__code__.co_filename, self.process.__code__.co_firstlineno))

        self._linkTypes = {self._fsHeader:self._processLink, self._zipHeader:self._processZiplink}

    def process(self, errorProcessing, chain, request, response, responseCnt, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Provide the file content as a response.
        '''
        assert isinstance(errorProcessing, Processing), 'Invalid processing %s' % errorProcessing
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        if request.method != GET:
            response.allows = GET
            response.code, response.text = METHOD_NOT_AVAILABLE, 'Path only available for GET'
        else:
            chain.proceed()
            # Make sure the given path points inside the repository
            entryPath = normOSPath(join(self.repositoryPath, normZipPath(unquote(request.uri))))
            if not entryPath.startswith(self.repositoryPath):
                response.code, response.text = RESOURCE_NOT_FOUND, 'Out of repository path'
            else:
                # Initialize the read file handler with None value
                # This will be set upon successful file open
                rf = None
                if isfile(entryPath):
                    rf, size = open(entryPath, 'rb'), os.path.getsize(entryPath)
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
                                        entry = self._linkTypes[linkType](subPath, *data)
                                        if entry is not None:
                                            rf, size = entry
                                            break
                            break
                        subLinkPath = dirname(linkPath)
                        if subLinkPath == linkPath:
                            break
                        linkPath = subLinkPath
        
                if rf is None:
                    response.code, response.text = METHOD_NOT_AVAILABLE, 'Invalid content resource'
                else:
                    response.code, response.text = RESOURCE_FOUND, 'Resource found'
                    responseCnt.source = rf
                    responseCnt.length = size
                    responseCnt.type, _encoding = guess_type(entryPath)
                    if not responseCnt.type: responseCnt.type = self.defaultContentType
                    return
        
        chain.branch(errorProcessing)

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
            return open(resPath, 'rb'), os.path.getsize(resPath)

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
            return zipFile.open(resPath, 'r'), zipFile.getinfo(resPath).file_size

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
