'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for localized messages sources.
'''

from ally.api.config import service, query
from ally.api.criteria import AsLike, AsEqual
from ally.internationalization import N_, textdomain
from introspection.api import modelDevel
from introspection.api.plugin import Plugin
from sql_alchemy.api.entity import Entity, QEntity, IEntityService
from introspection.api.component import Component
from datetime import datetime

# --------------------------------------------------------------------

textdomain('values')

TYPE_PYTHON = N_('python')
# The python type for the source
TYPE_JAVA_SCRIPT = N_('javascript')
# The java script type for the source
TYPES = (TYPE_PYTHON, TYPE_JAVA_SCRIPT)
# The available source types.

# --------------------------------------------------------------------

@modelDevel
class Source(Entity):
    '''
    Model for the source of the message, basically a file reference.
    '''
    Component = Component.Id
    Plugin = Plugin.Id
    Path = str
    Type = str
    LastModified = datetime
    
# --------------------------------------------------------------------

@query
class QSource(QEntity):
    '''
    Provides the query for the source.
    '''
    component = AsLike
    plugin = AsLike
    path = AsLike
    type = AsEqual

# --------------------------------------------------------------------

@service((Entity, Source), (QEntity, QSource))
class ISourceService(IEntityService):
    '''
    The source service.
    '''
