'''
Created on August 26, 2013

@package: superdesk tag
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for superdesk tags.
'''

from ally.api.config import service, query, call, LIMIT_DEFAULT
from ally.api.criteria import AsLike
from ally.support.api.keyed import Entity, QEntity, IEntityGetService, IEntityFindService
from superdesk.tag.api.type import TagType
from superdesk.api.domain_superdesk import modelData
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelData
class Tag(Entity):
    '''
    Provides the tag model.
    '''
    Type = TagType

# --------------------------------------------------------------------

@query(Tag)
class QTag(QEntity):
    '''
    Query for tag service
    '''
    key = AsLike

# --------------------------------------------------------------------

@service((Entity, Tag), (QEntity, QTag))
class ITagService(IEntityGetService, IEntityFindService):
    '''
    Tag model service interface
    '''

    @call
    def getAll(self, typeKey:TagType.Key=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QTag=None) -> Iter(Tag):
        '''
        Provides all the available tags.
        '''
