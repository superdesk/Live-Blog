'''
Created on Mar 8, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for group.
'''

from content.packager.api.domain_content import modelContent
from ally.support.api.entity import Entity, QEntity, IEntityService
from content.packager.api.reference import Reference
from ally.api.config import query, service
from ally.api.criteria import AsLike

# --------------------------------------------------------------------

@modelContent
class Group(Entity):
    '''
    Provides the group model.
    '''
    Role = str
    Mode = str

@modelContent
class GroupReference(Entity):
    '''
    Provides the group reference model.
    '''
    Group = Group
    Reference = Reference

# --------------------------------------------------------------------

@query(Group)
class QGroup(QEntity):
    '''
    Provides the group query.
    '''
    role = AsLike
    mode = AsLike

# --------------------------------------------------------------------

@service((Entity, Group))
class IGroupService(IEntityService):
    '''
    Provides the service methods for the group.
    '''

@service((Entity, GroupReference))
class IGroupReferenceService(IEntityService):
    '''
    Provides the service methods for the group reference.
    '''
