'''
Created on Sept 26, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''
from superdesk.meta.metadata_superdesk import Base
from ..api.article import Article
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, String

# --------------------------------------------------------------------

class ArticleMapped(Base, Article):
    '''
    Mapping for Article entity
    '''
    __tablename__ = 'article_demo'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')
    
    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    CreatedOn = Column('created_on', DateTime, nullable=False)
    Slug = Column('slug', String(255))
    
    
