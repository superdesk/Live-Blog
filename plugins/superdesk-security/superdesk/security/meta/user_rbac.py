'''
Created on Jan 21, 2013

@package: superdesk security
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for rbac user mappings.
'''

from security.rbac.meta.rbac import WithRbac
from sqlalchemy.schema import Column, ForeignKey
from superdesk.user.meta.user import UserMapped

# --------------------------------------------------------------------

class RbacUserMapped(UserMapped, WithRbac):
    '''
    Provides the mapping for user Rbac.
    '''
    __tablename__ = 'rbac_user'
    __table_args__ = dict(mysql_engine='InnoDB')

    # Non REST model attribute --------------------------------------
    userId = Column('fk_user_id', ForeignKey(UserMapped.userId, ondelete='CASCADE'), primary_key=True)
    
