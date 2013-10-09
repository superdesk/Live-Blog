'''
Created on May 2, 2012

@package: superdesk collaborator
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for source API.
'''

from ..api.collaborator import Collaborator
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.expression import case
from superdesk.meta.metadata_superdesk import Base
from superdesk.source.meta.source import SourceMapped
from superdesk.user.meta.user import UserMapped
from sql_alchemy.support.mapper import validate

# --------------------------------------------------------------------

@validate
class CollaboratorMapped(Base, Collaborator):
    '''Provides the mapping for Collaborator.'''
    __tablename__ = 'collaborator'
    __table_args__ = (UniqueConstraint('fk_user_id', 'fk_source_id', name='uix_user_source'),
                      dict(mysql_engine='InnoDB', mysql_charset='utf8'))

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    User = Column('fk_user_id', ForeignKey(UserMapped.userId, ondelete='CASCADE'))
    Source = Column('fk_source_id', ForeignKey(SourceMapped.Id, ondelete='RESTRICT'), nullable=False)
    @hybrid_property
    def Name(self):
        if self.User is None: return self.source.Name
        return self.user.FullName

    # Non REST model attributes --------------------------------------
    user = relationship(UserMapped, uselist=False, lazy='joined')
    source = relationship(SourceMapped, uselist=False, lazy='joined')

    # Expression for hybrid ------------------------------------
    Name.expression(lambda cls: case([(cls.User == None, SourceMapped.Name)], else_=UserMapped.FirstName))
