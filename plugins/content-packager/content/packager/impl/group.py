'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for group.
'''

from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from content.packager.api.group import IGroupService, IGroupReferenceService
from content.packager.meta.group import GroupMapped, GroupReferenceMapped

# --------------------------------------------------------------------

@setup(IGroupService, name='groupService')
class GroupServiceAlchemy(EntityServiceAlchemy, IGroupService):
    '''
    Implementation for @see: IGroupService
    '''

    def __init__(self):
        '''
        Construct the group service.
        '''
        EntityServiceAlchemy.__init__(self, GroupMapped)

@setup(IGroupReferenceService, name='groupReferenceService')
class GroupReferenceServiceAlchemy(EntityServiceAlchemy, IGroupReferenceService):
    '''
    Implementation for @see: IGroupReferenceService
    '''

    def __init__(self):
        '''
        Construct the group reference service.
        '''
        EntityServiceAlchemy.__init__(self, GroupReferenceMapped)
