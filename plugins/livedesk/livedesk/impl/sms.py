'''
Created on August 27, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy implementation for blog sms API.
'''
from ally.support.sqlalchemy.session import SessionSupport

# --------------------------------------------------------------------

@injected
@setup(IBlogSMSService, name='blogSMSService')
class BlogSMSServiceAlchemy(SessionSupport, IBlogCommentService):
    '''
    Implementation for @see: IBlogSMSService
    '''

    def __init__(self):
        '''
        Construct the blog sms service.
        '''

    def getMessages(self, blogId, sourceId=None, offset=None, limit=None, detailed=False, q=None):
        '''
        @see: IBlogSMSService.getMessages
        '''
        return ()
