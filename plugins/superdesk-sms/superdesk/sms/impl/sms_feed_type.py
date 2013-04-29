'''
Created on April 24, 2013

@package: feed sms
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for sms feed type API.
'''

from ..api.sms_feed_type import ISMSFeedTypeService
from ..meta.sms_feed_type import SMSFeedTypeMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.keyed import EntityGetServiceAlchemy, \
    EntityFindServiceAlchemy

# --------------------------------------------------------------------

@injected
@setup(ISMSFeedTypeService, name='smsFeedTypeService')
class SMSFeedTypeServiceAlchemy(EntityGetServiceAlchemy, EntityFindServiceAlchemy, ISMSFeedTypeService):
    '''
    Implementation for @see: ISMSFeedTypeService
    '''

    def __init__(self):
        '''
        Construct the sms feed type service.
        '''
        EntityGetServiceAlchemy.__init__(self, SMSFeedTypeMapped)
