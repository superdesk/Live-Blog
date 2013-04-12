'''
Created on Mar 7, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for localized files.
'''

from admin.api.domain_admin import modelAdmin
from admin.introspection.api.component import Component
from admin.introspection.api.plugin import Plugin
from ally.api.config import service, query
from ally.api.criteria import AsLikeOrdered, AsDateTimeOrdered
from ally.support.api.entity import Entity, QEntity, IEntityService
from datetime import datetime

# --------------------------------------------------------------------

@modelAdmin
class File(Entity):
    '''
    Model for the files.
    '''
    Component = Component
    Plugin = Plugin
    Path = str
    LastModified = datetime

# --------------------------------------------------------------------

@query(File)
class QFile(QEntity):
    '''
    Provides the query for the files.
    '''
    component = AsLikeOrdered
    plugin = AsLikeOrdered
    path = AsLikeOrdered
    lastModified = AsDateTimeOrdered

# --------------------------------------------------------------------

@service((Entity, File), (QEntity, QFile))
class IFileService(IEntityService):
    '''
    The files service.
    '''
