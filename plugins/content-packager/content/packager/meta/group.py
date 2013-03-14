'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

Contains SQL alchemy meta for group API.
'''

from ally.support.sqlalchemy.mapper import validate
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.types import String
from content.packager.api.group import Group, GroupReference
from content.packager.meta.reference import ReferenceMapped

# --------------------------------------------------------------------

@validate(exclude=['Id'])
class GroupMapped(Base, Group):
    '''
    Provides the mapping for Group.
    '''
    __tablename__ = 'content_group'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', String(100), nullable=False, primary_key=True)
    Role = Column('role', String(255))
    Mode = Column('mode', String(255))

@validate
class GroupReferenceMapped(Base, GroupReference):
    '''
    Provides the mapping for GroupMapped.
    '''
    __tablename__ = 'content_group_reference'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Group = Column('fk_group_id', ForeignKey(GroupMapped.Id, ondelete='RESTRICT'), nullable=False)
    Reference = Column('fk_reference_id', ForeignKey(ReferenceMapped.Id, ondelete='RESTRICT'), nullable=False)
