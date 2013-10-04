'''
Created on Aug 23, 2011

@package superdesk
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for language API.
'''

from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base

# --------------------------------------------------------------------

class LanguageAvailable(Base):
    '''
    Provides the mapping for @see: Language.
    '''
    __tablename__ = 'language'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')
    
    id = Column('id', INTEGER(unsigned=True), primary_key=True)
    code = Column('code', String(20), nullable=False, unique=True)
