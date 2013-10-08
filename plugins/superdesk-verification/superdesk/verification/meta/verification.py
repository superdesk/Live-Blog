'''
Created on Oct 3, 2013

@package: superdesk post PostVerification
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for post PostVerification status API.
'''

from ..api.verification import PostVerification
from superdesk.meta.metadata_superdesk import Base
from superdesk.user.meta.user import UserMapped
from superdesk.verification.meta.status import VerificationStatusMapped
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.orm import relationship, column_property
from superdesk.post.meta.post import PostMapped
from sqlalchemy.sql.expression import select

# --------------------------------------------------------------------

class PostVerificationMapped(Base, PostVerification):
    '''
    Provides the mapping for PostType.
    '''
    __tablename__ = 'post_verification'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('fk_post_id', ForeignKey(PostMapped.Id, ondelete='CASCADE'), primary_key=True)
    Status = association_proxy('status', 'Key')
    Checker = Column('fk_user_id', ForeignKey(UserMapped.Id, ondelete='RESTRICT'), nullable=True)
    # None REST model attribute --------------------------------------
    statusId = Column('fk_status_id', ForeignKey(VerificationStatusMapped.id, ondelete='RESTRICT'), nullable=True)
    status = relationship(VerificationStatusMapped, uselist=False, lazy='joined')
    #post = relationship(PostMapped, uselist=False, backref='verification', lazy='joined')

PostMapped.PostVerification = column_property(select([PostMapped.Id], whereclause=PostMapped.Id==PostVerificationMapped.Id)) #
