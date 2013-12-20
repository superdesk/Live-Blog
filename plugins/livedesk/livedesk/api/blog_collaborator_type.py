'''
Created on Dec 20, 2013

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog collaborator type.
'''

from ally.api.config import service
from ally.api.option import SliceAndTotal  # @UnusedImport
from ally.support.api.entity import IEntityNQPrototype
from gui.action.api.category import IActionCategoryPrototype
from livedesk.api.domain_livedesk import modelLiveDesk


# --------------------------------------------------------------------
@modelLiveDesk(id='Name')
class BlogCollaboratorType:
    '''
    Provides the blog collaborator type.
    '''
    Name = str
    IsDefault = bool

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service(('Entity', BlogCollaboratorType))
class IBlogCollaboratorTypeService(IEntityNQPrototype):
    '''
    Provides the service methods for the blog collaborator types.
    '''
    
@service(('CATEGORY', BlogCollaboratorType))
class IBlogCollaboratorTypeActionService(IActionCategoryPrototype):
    '''
    Provides the service for associating actions to blog type.
    '''
