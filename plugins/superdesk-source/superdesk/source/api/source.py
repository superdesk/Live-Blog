'''
Created on May 2, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for source. A source provides content, the source type of a source dictates the format in which
the content is received from the source.
'''

from .type import SourceType
from ally.api.config import service, call, query
from ally.api.criteria import AsBoolean, AsLikeOrdered, AsLike, AsEqual
from ally.api.type import Iter, Reference
from superdesk.api.domain_superdesk import modelData
from ally.support.api.entity_ided import Entity, QEntity, IEntityGetCRUDService

# --------------------------------------------------------------------

@modelData
class Source(Entity):
    '''
    Provides the source model.
    '''
    Type = SourceType
    Name = str
    URI = Reference
    Key = str
    IsModifiable = bool
    OriginName = str
    OriginURI = str

# --------------------------------------------------------------------

@query(Source)
class QSource(QEntity):
    '''
    Provides the query for source model.
    '''
    name = AsLikeOrdered
    uri = AsLikeOrdered
    isModifiable = AsBoolean
    all = AsLike
    type = AsEqual

# --------------------------------------------------------------------

@service((Entity, Source), (QEntity, QSource))
class ISourceService(IEntityGetCRUDService):
    '''Provides the service methods for the source.'''

    @call
    def getAll(self, typeKey:SourceType.Key=None, q:QEntity=None, **options:SliceAndTotal) -> Iter(Source.Id):
        '''Returns a list of source identifiers based on the given filters.

        :param: typeKey: SourceType.Key
            The source type to filter by.
        :param: q: Query|None
            The query to search by.
        :param: options: @see: SliceAndTotal
            The options to fetch the entities with.
        :return: Iterable(Source.Id)
            The iterable with the source identifiers.
        '''
