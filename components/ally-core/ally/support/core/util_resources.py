'''
Created on Jan 4, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods based on the specifications.
'''

from ..api.util_type import isPropertyTypeId
from ally.api.operator import Property
from ally.core.spec.resources import ResourcesManager

# --------------------------------------------------------------------
 
def pathsFor(resourcesManager, properties, basePath):
    '''
    Extracts the paths that are linked with the provided properties. Basically any property that represents the id
    property type for a model is searched for a path.
    
    @param resourcesManager: ResourcesManager
        The resource manager used for searching the paths.
    @param properties: list[Property]
        The list of properties to search in.
    @param basePath: Path
        The base bath to perform the search from.
    '''
    assert isinstance(resourcesManager, ResourcesManager), 'Invalid resource manager %s' % resourcesManager
    assert isinstance(properties, list), 'Invalid properties list %s' % properties
    paths = {}
    for prop in properties:
        assert isinstance(prop, Property)
        if isPropertyTypeId(prop.type):
            path = resourcesManager.findGetModel(basePath, prop.type.model)
            if path is not None:
                paths[prop.name] = path
    return paths