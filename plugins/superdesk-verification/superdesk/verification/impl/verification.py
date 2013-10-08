'''
Created on Oct 3, 2013

@package: superdesk post verification
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy implementation for post PostVerification API.
'''

from ..api.verification import IPostVerificationService
from ..meta.verification import PostVerificationMapped
from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy

# --------------------------------------------------------------------

@injected
@setup(IPostVerificationService, name='postVerificationService')
class PostVerificationServiceAlchemy(EntityServiceAlchemy, IPostVerificationService):
    '''
    Implementation for @see: IPostVerificationService
    '''

    def __init__(self):
        '''
        Construct the post PostVerification status service.
        '''
        EntityServiceAlchemy.__init__(self, PostVerificationMapped)
        
        
        
#                 if checkerId or statusId: 
#             sql = sql.join(PostVerificationMapped)
#             if checkerId: sql = sql.filter(PostVerificationMapped.Checker == checkerId)
#             if statusId: sql = sql.filter(PostVerificationMapped.Status == statusId)