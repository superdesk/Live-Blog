'''
Created on Oct 22, 2013

@package: frontline
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

API specifications for SMS sync.
'''

from ally.support.api.entity import Entity, IEntityService, QEntity
from ally.api.config import query, service, call
from ally.api.criteria import AsRangeOrdered
from superdesk.source.api.source import Source
from frontline.api.domain_sms import modelSMS
from livedesk.api.blog import Blog

# --------------------------------------------------------------------

@modelSMS
class SmsSync(Entity):
    '''
    Provides the Sms sync model.
    '''
    Blog = Blog
    Source = Source
    LastId = int

# --------------------------------------------------------------------

@query(SmsSync)
class QSmsSync(QEntity):
    '''
    Provides the query for SmsSync.
    '''
    lastId = AsRangeOrdered

# --------------------------------------------------------------------

@service((Entity, SmsSync), (QEntity, QSmsSync))
class ISmsSyncService(IEntityService):
    '''
    Provides the service methods for the Sms sync.
    '''
    
    @call
    def getSmsSyncByBlogAndSource(self, blog:Blog.Id, source:Source.Id) -> SmsSync:
        '''
        Returns the Sms sync model for the given blog and source.

        @param blog: Blog.Id
            The  identifier
        @param source: Source.Id
            The source identifier
        '''
