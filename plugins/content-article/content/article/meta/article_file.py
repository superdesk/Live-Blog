'''
Created on Mar 14, 2013

@package: content article file
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

Contains SQL alchemy meta for article file API.
'''

from ally.support.sqlalchemy.mapper import validate
from superdesk.meta.metadata_superdesk import Base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.dialects.mysql.base import INTEGER
from content.article.api.article_file import ArticleFile
from content.article.meta.article import ArticleMapped
from superdesk.media_archive.meta.meta_data import MetaDataMapped

# --------------------------------------------------------------------

@validate
class ArticleFileMapped(Base, ArticleFile):
    '''
    Provides the mapping for ArticleFile.
    '''
    __tablename__ = 'article_file'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Article = Column('fk_article_id', ForeignKey(ArticleMapped.Id, ondelete='CASCADE'), nullable=False)
    MetaData = Column('fk_metadata_id', ForeignKey(MetaDataMapped.Id, ondelete='CASCADE'), nullable=False)
