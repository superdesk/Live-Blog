'''
Created on May 22, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Contains the SQL alchemy meta for blog configurations API.
'''

from superdesk.meta.metadata_superdesk import Base
from ally.support.sqlalchemy.mapper import validate
from support.api.configuration import Configuration
from support.meta.configuration import ConfigurationDescription
from livedesk.meta.blog import BlogMapped
from sqlalchemy.schema import Column, ForeignKey

# --------------------------------------------------------------------

@validate(exclude=('Name',))
class BlogConfigurationMapped(Base, ConfigurationDescription, Configuration):
    __tablename__ = 'blog_configuration'

    parent = Column('fk_blog_id', ForeignKey(BlogMapped.Id, ondelete='CASCADE'), primary_key=True)
