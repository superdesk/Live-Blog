'''
Created on Sept 26, 2012

@package ally core request
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu
'''
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Text
from superdesk.article.meta.article import ArticleMapped
from ..api.article_ctx import ArticleCtx

# --------------------------------------------------------------------

class ArticleCtxMapped(Base, ArticleCtx):
    '''
    Mapping for Article entity
    '''
    __tablename__ = 'article_ctx_demo'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')
    
    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Article = Column('fk_article_id', ForeignKey(ArticleMapped.Id), nullable=False)
    Content = Column('content', Text)
    Type = Column('type', INTEGER(unsigned=True))
    
    