'''
Created on May 22, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for blog configurations API.
'''

from ..api.configuration import BlogConfiguration
from superdesk.meta.metadata_superdesk import Base
from ally.support.sqlalchemy.mapper import validate
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String

# --------------------------------------------------------------------

@validate
class BlogConfigurationMapped(Base, ConfigurationDescription, Configuration):
    __tablename__ = 'blog_configuration'
    parent = Column('fk_blog_id', ForeignKey(BlogMapped.Id, ondelete='CASCADE'), primary_key=True)



