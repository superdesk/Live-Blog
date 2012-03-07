'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for localized messages sources.
'''

from .file import File, QFile
from ally.api.config import service, query
from ally.api.criteria import AsEqual
from ally.internationalization import N_, textdomain
from introspection.api import modelDevel
from sql_alchemy.api.entity import Entity, QEntity, IEntityService

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
class Source(File):
    '''
    Model for the source of the message, basically a file reference.
    '''
    Type = str
    
# --------------------------------------------------------------------

@query
class QSource(QFile):
    '''
    Provides the query for the source.
    '''
    type = AsEqual

# --------------------------------------------------------------------

@service((Entity, Source), (QEntity, QSource))
class ISourceService(IEntityService):
    '''
    The sources service.
    '''
