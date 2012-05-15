'''
Created on May 9, 2012

@package: ally authentication
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides authentication support.
'''

from .operator.authentication.convert import asAuthenticated
from .operator.type import TypeModel, TypeModelProperty
from .type import typeFor, Type

# --------------------------------------------------------------------

def auth(type):
    '''
    Converts the provided type to a authentication type.
    '''
    if isinstance(type, Type): typ = type
    else:
        typ = typeFor(type)
        assert typ is not None, 'Invalid type %s' % type

    if isinstance(typ, TypeModel): return asAuthenticated(typ)

    if isinstance(typ, TypeModelProperty):
        assert isinstance(typ, TypeModelProperty)
        return typeFor(getattr(asAuthenticated(typ.parent).forClass, typ.property))

    raise TypeError('Invalid type %s to mark as authenticated' % typ)
