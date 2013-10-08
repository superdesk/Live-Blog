'''
Created on Oct 3, 2013

@package: superdesk post verification
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

The API specifications for the post verification.
'''

from ally.api.config import service
from ally.support.api.entity import Entity, IEntityNQService

from superdesk.api.domain_superdesk import modelData
from superdesk.user.api.user import User
from superdesk.verification.api.status import VerificationStatus


# --------------------------------------------------------------------
@modelData
class PostVerification(Entity):
    '''    
    Provides the post verification.
    '''
    # TODO: add after migration: Post = Post
    Status = VerificationStatus
    Checker = User

# --------------------------------------------------------------------

@service((Entity, PostVerification))
class IPostVerificationService(IEntityNQService):
    '''
    Post verification model service interface
    '''

