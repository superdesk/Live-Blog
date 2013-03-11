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

# --------------------------------------------------------------------

@setup(IGroupService, name='groupService')
class GroupServiceAlchemy(EntityServiceAlchemy, IGroupService):
    '''
    Implementation for @see: IGroupService
    '''

@setup(IGroupReferenceService, name='groupReferenceService')
class GroupReferenceServiceAlchemy(EntityServiceAlchemy, IGroupReferenceService):
    '''
    Implementation for @see: IGroupReferenceService
    '''
