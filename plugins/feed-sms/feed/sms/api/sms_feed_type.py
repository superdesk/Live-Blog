'''
Created on April 24, 2013

@package: feed sms
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for sms feed types.
'''

from ally.api.config import service
from ally.support.api.keyed import Entity, IEntityService
from feed.api.domain_feed import modelFeed

# --------------------------------------------------------------------

@modelFeed
class SMSFeedType(Entity):
    '''
    Provides the sms feed type model.
    '''
    Active = bool

# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------

@service((Entity, SMSFeedType))
class ISMSFeedTypeService(IEntityService):
    '''
    Provides the service methods for the task link types.
    '''
