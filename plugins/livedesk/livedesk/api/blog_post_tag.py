'''
Created on August 26, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for livedesk blog post tags.
'''

from ally.api.config import service, query, call
from ally.api.criteria import AsLike
from ally.support.api.entity import Entity, IEntityService, QEntity
from superdesk.tag.api.type import TagType
#from superdesk.api.domain_superdesk import modelData

# --------------------------------------------------------------------

@modelData
class Tag(Entity):
    '''
    Provides the user model.
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
               q:QTag=None) -> Iter(Source):
        '''
        Provides all the available tags.
        '''
