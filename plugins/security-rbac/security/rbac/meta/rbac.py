'''
Created on Dec 21, 2012

@package: security - role based access control
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for rbac APIs.
'''

from ..api.rbac import Rbac, Role
from security.meta.metadata_security import Base
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String
from ally.support.sqlalchemy.mapper import validate

# --------------------------------------------------------------------

class RbacMapped(Base, Rbac):
    '''
    Provides the mapping for base Rbac.
    '''
    __tablename__ = 'rbac'
    __table_args__ = dict(mysql_engine='InnoDB')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)

@validate
class RoleMapped(RbacMapped, Role):
    '''
    Provides the mapping for Role rbac.
    '''
    __tablename__ = 'rbac_role'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Name = Column('name', String(100), nullable=False, unique=True)
    Description = Column('description', String(255))
    # Non REST model attribute --------------------------------------
    rbacId = Column('fk_rbac_id', ForeignKey(RbacMapped.Id, ondelete='CASCADE'), primary_key=True)
