'''
Created on Aug 25, 2011

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for article type API.
'''

from . import meta
from ..api.article_type import ArticleType
from ally.support.sqlalchemy.mapper import mapperModel
from sqlalchemy.schema import Table, Column
from sqlalchemy.types import String, Integer

# --------------------------------------------------------------------

table = Table('article_type', meta,
              Column('id', Integer, primary_key=True, key='Id'),
              Column('name', String(255), nullable=False, unique=True, key='Name'))

ArticleType = mapperModel(ArticleType, table)
