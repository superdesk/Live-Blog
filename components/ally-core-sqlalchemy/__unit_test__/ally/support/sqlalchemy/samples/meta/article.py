'''
Created on Aug 25, 2011

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for article API.
'''

from . import meta
from ..api.article import Article
from .article_type import ArticleType
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import String, Integer

# --------------------------------------------------------------------

table = Table('article', meta,
              Column('id', Integer, primary_key=True, key='Id'),
              Column('fk_article_type_id', ForeignKey(ArticleType.Id), nullable=False, key='Type'),
              Column('name', String(255), nullable=False, key='Name'))

Article = mapperModel(Article, table)
