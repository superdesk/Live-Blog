'''
Created on May 28, 2013

@package: support
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Provides file-info links API support that can be binded to other entities.
'''

from ally.api.config import service, call, LIMIT_DEFAULT, INSERT, DELETE
from ally.api.type import Iter
from ally.support.api.entity import Entity
from superdesk.media_archive.api.meta_info.py import MetaInfo, QMetaInfo

# TODO: on DELETE here, should we delete the file, along the file link?
#   may be when there is no other usage of that file, alike in Newscoop

# --------------------------------------------------------------------

# No model

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service
class IFileLinkService:
    '''
    Provides the file link service.
    '''

    @call
    def getById(self, parentId:Entity.Id, fileInfoId:MetaInfo.Id) -> MetaInfo:
        '''
        Provides the file info based on the parentId and file info.

        @param parentId: integer
            The id of the entity which the file info is linked to.
        @param fileInfo: integer
            The id of the file info to be taken.
        @raise InputError: If the parentId is not valid. 
        '''

    @call
    def getAll(self, parentId:Entity.Id, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QMetaInfo=None) -> Iter(MetaInfo):
        '''
        Provides the file infos relating the parentId.
        '''

    @call(method=INSERT, webName='File')
    def attachFile(self, parentId:Entity.Id, fileInfoId:MetaInfo.Id):
        '''
        Attaches file info to the parentId
        '''

    @call(method=DELETE, webName='File')
    def detachFile(self, parentId:Entity.Id, fileInfoId:MetaInfo.Id) -> bool:
        '''
        Detaches file info from the parentId
        '''
