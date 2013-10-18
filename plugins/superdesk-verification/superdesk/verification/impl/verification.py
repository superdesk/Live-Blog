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
<<<<<<< HEAD
from superdesk.verification.api.verification import PostVerification
from ally.support.sqlalchemy.util_service import handle
from sqlalchemy.exc import SQLAlchemyError
from ally.exception import InputError, Ref
from sqlalchemy.orm.exc import NoResultFound
from ally.support.api.util_service import copy
from superdesk.verification.meta.status import VerificationStatusMapped
=======
>>>>>>> 4d49bcc09513d2bb06041f30e41a8e7ce2d74ffe

# --------------------------------------------------------------------

@injected
@setup(IPostVerificationService, name='postVerificationService')
class PostVerificationServiceAlchemy(EntityServiceAlchemy, IPostVerificationService):
    '''
    Implementation for @see: IPostVerificationService
    '''
<<<<<<< HEAD
    
    default_verification_status_key = 'nostatus'
=======
>>>>>>> 4d49bcc09513d2bb06041f30e41a8e7ce2d74ffe

    def __init__(self):
        '''
        Construct the post PostVerification status service.
        '''
        EntityServiceAlchemy.__init__(self, PostVerificationMapped)
        
        
<<<<<<< HEAD
    def insert(self, postVerification):
        '''
        @see: IPostVerificationService.insert
        '''
        assert isinstance(postVerification, PostVerification), 'Invalid post verification %s' % postVerification

        postVerificationDb = PostVerificationMapped()
        postVerificationDb.statusId = self._verificationStatusId(postVerification.Status)
        try:
            self.session().add(copy(postVerification, postVerificationDb, exclude=('Status',)))
            self.session().flush((postVerificationDb,))
        except SQLAlchemyError as e: handle(e, postVerificationDb)
        postVerification.Id = postVerificationDb.Id
        return postVerification.Id

    def update(self, postVerification):
        '''
        @see: IPostVerificationService.update
        '''
        assert isinstance(postVerification, PostVerification), 'Invalid post verification %s' % postVerification

        postVerificationDb = self.session().query(PostVerificationMapped).get(postVerification.Id)
        if not postVerificationDb:
            assert isinstance(postVerificationDb, PostVerificationMapped), 'Invalid post verification %s' % postVerificationDb
            raise InputError(Ref(_('Unknown post verification id'), ref=PostVerification.Id))
        try:
            postVerificationDb.statusId = self._verificationStatusId(postVerification.Status)
            self.session().flush((copy(postVerification, postVerificationDb, exclude=('Status',)),))
        except SQLAlchemyError as e: handle(e, postVerificationDb)
        
        
    # ----------------------------------------------------------------

    def _verificationStatusId(self, key):
        '''
        Provides the verification status id that has the provided key.
        '''
        
        if not key: key = self.default_verification_status_key

        try:
            sql = self.session().query(VerificationStatusMapped.id).filter(VerificationStatusMapped.Key == key)
            return sql.one()[0]
        except NoResultFound:
            raise InputError(Ref(_('Invalid verification status %(verificationStatus)s') % dict(verificationStatus=key), ref=PostVerificationMapped.Status))  
        
=======
        
#                 if checkerId or statusId: 
#             sql = sql.join(PostVerificationMapped)
#             if checkerId: sql = sql.filter(PostVerificationMapped.Checker == checkerId)
#             if statusId: sql = sql.filter(PostVerificationMapped.Status == statusId)
>>>>>>> 4d49bcc09513d2bb06041f30e41a8e7ce2d74ffe
