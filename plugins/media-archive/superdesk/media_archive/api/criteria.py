'''
Created on Dec 13, 2012

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan-Vasile Pocol

Provides custom criteria for media archive multiplugin archive.
'''

from ally.api.config import criteria
from ally.api.criteria import AsOrdered, AsLike, AsEqual, AsBoolean, AsRange, \
    AsDate, AsDateTime, AsDateTimeOrdered, AsTime, AsTimeOrdered, AsDateOrdered, \
    AsRangeOrdered, AsLikeOrdered, AsEqualOrdered, AsBooleanOrdered
from ally.api.type import List

# --------------------------------------------------------------------

@criteria
class AsOperator:
    '''
    Provides the option to set how different criteria are combined for the query. The operator(op) can have
    the following values:

    and - include - means that the value is mandatory for the given criteria
    or - extend - means that the value is optional for the given criteria
    not - exclude - means that the value if forbidden for the given criteria

    The query compose an and condition with all and criteria, and all negated not criteria. Then is made an or with all
    or criteria
    '''
    op = str

# --------------------------------------------------------------------

@criteria
class AsLikeExpression:
    '''
    Provides query for properties that can be managed by a like function, this will only handle string types
    Also provides the boolean expression functionality, that in case of like string operator can had in the same all conditions
    '''

    #include - the list of included values
    inc = List(str)
    #extend - the list of extended values
    ext = List(str)
    #exclude - the list of excluded values
    exc = List(str)

# --------------------------------------------------------------------

@criteria
class AsLikeExpressionOrdered(AsOrdered):
    '''
    Provides the like search and also the ordering and boolean expression functionality (see AsOperator).
    '''

    #include - the list of included values
    inc = List(str)
    #extend - the list of extended values
    ext = List(str)
    #exclude - the list of excluded values
    exc = List(str)

# --------------------------------------------------------------------

@criteria
class AsEqualExpression(AsEqual, AsOperator):
    '''
    Provides query for properties that can be managed by a equal function, this will only handle string types.
    Also provides the boolean expression functionality (see AsOperator).
    '''
# --------------------------------------------------------------------

@criteria
class AsEqualExpressionOrdered(AsEqualOrdered, AsOperator):
    '''
    Provides the equal search and also the ordering and boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria
class AsBooleanExpression(AsBoolean, AsOperator):
    '''
    Provides query for properties that can be managed as booleans.
    Also provides the boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria
class AsBooleanExpressionOrdered(AsBooleanOrdered, AsOperator):
    '''
    Provides the booleans search and also the ordering and boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria
class AsRangeExpression(AsRange, AsOperator):
    '''
    Provides a query for properties that need to be handled as a range.
    Also provides the boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria
class AsRangeExpressionOrdered(AsRangeOrdered, AsOperator):
    '''
    Provides the equal search and also the ordering and boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria
class AsDateExpression(AsDate, AsOperator):
    '''
    Provides query for properties that can be managed as date.
    Also provides the boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria
class AsDateExpressionOrdered(AsDateOrdered, AsOperator):
    '''
    Provides the date search and also the ordering and boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria
class AsTimeExpression(AsTime, AsOperator):
    '''
    Provides query for properties that can be managed as time.
    Also provides the boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria
class AsTimeExpressionOrdered(AsTimeOrdered, AsOrdered):
    '''
    Provides the time search and also the ordering and boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria
class AsDateTimeExpression(AsDateTime, AsOperator):
    '''
    Provides query for properties that can be managed as date time.
    Also provides the boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria
class AsDateTimeExpressionOrdered(AsDateTimeOrdered, AsOperator):
    '''
    Provides the date time search and also the ordering and boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria(main='values')
class AsIn:
    '''
    Provides query for properties that can be managed by 'IN' function applied to a list.
    '''

    values = List(str)

# --------------------------------------------------------------------

@criteria
class AsInExpression(AsIn, AsOperator):
    '''
    Provides query for properties that can be managed by 'IN' function applied to a list.
    Also provides the boolean expression functionality (see AsOperator).
    '''

# --------------------------------------------------------------------

@criteria(main='values')
class AsInOrdered(AsIn, AsOrdered):
    '''
    Provides query for properties that can be managed by 'IN' function applied to a list.
    Also provides the ordering functionality.
    '''

# --------------------------------------------------------------------

@criteria
class AsInExpressionOrdered(AsInOrdered, AsOperator):
    '''
    Provides query for properties that can be managed by 'IN' function applied to a list.
    Also provides the ordering and boolean expression functionality (see AsOperator).
    '''
