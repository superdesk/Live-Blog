'''
Created on Dec 13, 2012

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan-Vasile Pocol

Provides custom criteria for media archive multiplugin archive.
'''

from ally.api.config import criteria
from ally.api.criteria import AsOrdered
from ally.api.type import List

# --------------------------------------------------------------------

@criteria
class AsLikeExpression:
    '''
    Provides query for properties that can be managed by a like function, this will only handle string types
    Also provides the boolean expression functionality, that in case of like string operator can had in the same all conditions

    inc - include - means that the value is mandatory for the given criteria
    ext - extend - means that the value is optional for the given criteria
    exc - exclude - means that the value if forbidden for the given criteria

    The query compose an 'and' condition with all 'inc' criteria, and all negated 'exc' criteria. Then it is made an or with all
    'ext' criteria
    '''

    #include - the list of included values
    inc = List(str)
    #extend - the list of extended values
    ext = List(str)
    #exclude - the list of excluded values
    exc = List(str)

# --------------------------------------------------------------------

@criteria
class AsLikeExpressionOrdered(AsLikeExpression, AsOrdered):
    '''
    Provides the like search and also the ordering and boolean expression functionality (see AsLikeExpression).
    '''

# --------------------------------------------------------------------

@criteria(main='values')
class AsIn:
    '''
    Provides query for properties that can be managed by 'IN' function applied to a list.
    '''

    values = List(str)

# --------------------------------------------------------------------

@criteria(main='values')
class AsInOrdered(AsIn, AsOrdered):
    '''
    Provides query for properties that can be managed by 'IN' function applied to a list.
    Also provides the ordering functionality.
    '''
