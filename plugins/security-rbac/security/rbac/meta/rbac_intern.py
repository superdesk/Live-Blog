'''
Created on Dec 21, 2012

@package: security - role based access control
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for rbac internal mappings.
'''

from .rbac import RbacMapped, RoleMapped
from security.meta.metadata_security import Base
from security.meta.right import RightMapped
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey

# --------------------------------------------------------------------

class RoleNode(Base):
    '''
    Provides the mapping for roles hierarchy.
    '''
    __tablename__ = 'rbac_role_node'
    __table_args__ = dict(mysql_engine='InnoDB')

    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    role = Column('fk_role_id', ForeignKey(RoleMapped.Id))
    left = Column('lft', INTEGER, nullable=False)
    right = Column('rgt', INTEGER, nullable=False)

class RbacRight(Base):
    '''
    Provides the mapping for role right Rbac.
    '''
    __tablename__ = 'rbac_rbac_right'
    __table_args__ = dict(mysql_engine='InnoDB')

    rbac = Column('fk_rbac_id', ForeignKey(RbacMapped.Id), primary_key=True)
    right = Column('fk_right_id', ForeignKey(RightMapped.Id), primary_key=True)

class RbacRole(Base):
    '''
    Provides the mapping for user role Rbac.
    '''
    __tablename__ = 'rbac_rbac_role'
    __table_args__ = dict(mysql_engine='InnoDB')

    rbac = Column('fk_rbac_id', ForeignKey(RbacMapped.Id), primary_key=True)
    role = Column('fk_role_id', ForeignKey(RoleMapped.Id), primary_key=True)
