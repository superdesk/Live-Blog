'''
Created on Jan 4, 2012

@package: support acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides ACL utility methods for resources.
'''

from ally.api.operator.type import TypeProperty
from ally.core.spec.resources import Invoker, Path
from ally.http.spec.server import IEncoderPath
from ally.support.core.util_resources import propertyTypesOf, \
    ReplacerWithMarkers
import re

# --------------------------------------------------------------------

def processPath(path, invoker, encoder, values=None):
    '''
    Process the gateway path marking groups for all property types present in the path.
    
    @param path: Path
        The path to process as a gateway pattern.
    @param invoker: Invoker
        The invoker to process the pattern based on.
    @param encoder: IEncoderPath
        The path encoder used for processing to path.
    @param values: dictionary{TypeProperty: string}
        The static values to be placed on the path, as a key the type property that has the value.
    @return: tuple(string, list[TypeProperty])
        Returns the gateway path and the property types that the path has markers for.
    '''
    assert isinstance(path, Path), 'Invalid path %s' % path
    assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
    assert isinstance(encoder, IEncoderPath), 'Invalid path encoder %s' % encoder
    
    replaceMarkers, types = [], []
    for propertyType in propertyTypesOf(path, invoker):
        assert isinstance(propertyType, TypeProperty), 'Invalid property type %s' % propertyType
        
        if values:
            assert isinstance(values, dict), 'Invalid values %s' % values
            value = values.get(propertyType)
            if value is not None:
                assert isinstance(value, str), 'Invalid value %s' % value
                replaceMarkers.append(value)
                continue
            
        replaceMarkers.append('{%s}' % len(types))
        types.append(propertyType)
    
    return encoder.encode(path, invalid=ReplacerWithMarkers().register(replaceMarkers)), types

def processPattern(path, invoker, encoder, values=None):
    '''
    Process the gateway pattern creating groups for all property types present in the path.
    
    @param path: Path
        The path to process as a gateway pattern.
    @param invoker: Invoker
        The invoker to process the pattern based on.
    @param encoder: IEncoderPath
        The path encoder used for processing to path.
    @param values: dictionary{TypeProperty: string}
        The static values to be placed on the path, as a key the type property that has the value.
    @return: tuple(string, list[TypeProperty])
        Returns the gateway pattern and the property types that the pattern has capturing groups for.
    '''
    assert isinstance(path, Path), 'Invalid path %s' % path
    assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
    assert isinstance(encoder, IEncoderPath), 'Invalid path encoder %s' % encoder
    
    replaceMarkers, types = [], []
    for propertyType in propertyTypesOf(path, invoker):
        assert isinstance(propertyType, TypeProperty), 'Invalid property type %s' % propertyType
        
        if values:
            assert isinstance(values, dict), 'Invalid values %s' % values
            value = values.get(propertyType)
            if value is not None:
                assert isinstance(value, str), 'Invalid value %s' % value
                replaceMarkers.append(re.escape(value))
                continue
            
        if propertyType.isOf(int): replaceMarkers.append('([0-9\\-]+)')
        elif propertyType.isOf(str): replaceMarkers.append('([^\\/]+)')
        else: raise Exception('Unusable type \'%s\'' % propertyType)
        types.append(propertyType)
    
    pattern = encoder.encodePattern(path, invalid=ReplacerWithMarkers().register(replaceMarkers))
    return '%s[\\/]?(?:\\.|$)' % pattern, types
