'''
Created on August 26, 2013

@package: superdesk tag
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for superdesk tags API.
'''

from superdesk.tag.api.type import QTag, ITagTypeService
from superdesk.tag.meta.tag import TagMapped
from superdesk.tag.meta.type import TagTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.keyed import EntityGetServiceAlchemy, EntityFindServiceAlchemy
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from ally.api.extension import IterPart

# --------------------------------------------------------------------

@injected
@setup(ITagService, name='tagService')
class TagServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, ITagService):
    '''
    Implementation for @see: ITagService
    '''

    def __init__(self):
        '''
        Construct the tag service.
        '''
        EntityGetServiceAlchemy.__init__(self, TagMapped, QTag)

    def getAll(self, typeKey=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: ITagService.getAll
        '''
        sql = self.session().query(TagMapped)
        if typeKey:
            sql = sql.join(TagTypeMapped).filter(TagTypeMapped.Key == typeKey)
        if q:
            assert isinstance(q, QTag), 'Invalid tag query %s' % q
            sql = buildQuery(sql, q, TagMapped)
        sql = sql.order_by(TagMapped.Key)

        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()
