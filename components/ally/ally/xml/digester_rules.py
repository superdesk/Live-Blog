'''
Created on Mar 9, 2012

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides an XML digester general rules.
'''

from .digester import Rule, Digester

# --------------------------------------------------------------------

class RuleCreate(Rule):
    '''
    Rule that creates and pushes on the digester stack a value at the begin event and then at the end pulls the value from
    the stack.
    '''

    def __init__(self, create):
        '''
        Construct the push rule.
        
        @param create: callable()
            The callable that provides the value to push on the stack, the callable has to take no parameters.
        @param end: callable(object)|None
            The callable that is notified at the end when the object is pulled from the stack, the callable will take a
            parameter whcih is the pulled object.
        '''
        assert callable(create), 'Invalid create callable %s' % create
        self._create = create

    def begin(self, digester, **attributes):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, Digester), 'Invalid digester %s' % digester
        digester.stack.append(self._create())

    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(digester, Digester), 'Invalid digester %s' % digester
        digester.stack.pop()

class RuleSet(Rule):
    '''
    Rule that sets on a stack object another stack object based on a provided callable that will manage the set.
    The set is performed at the end event.
    '''

    def __init__(self, setter, toIndex= -2, fromIndex= -1):
        '''
        Construct the set rule.
        
        @param setter: callable(object, object)
            The callable used to set the second object to the first object.
        @param toIndex: integer
            The index to which to set the from stack value object.
        @param fromIndex: integer
            The index from which to take the stack value object.
        '''
        assert callable(setter), 'Invalid setter callable %s' % setter
        assert isinstance(toIndex, int), 'Invalid to index %s' % toIndex
        assert isinstance(fromIndex, int), 'Invalid from index %s' % fromIndex
        self._setter = setter
        self._toIndex = toIndex
        self._fromIndex = fromIndex

    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(digester, Digester), 'Invalid digester %s' % digester
        self._setter(digester.stack[self._toIndex], digester.stack[self._fromIndex])

class RuleSetContent(Rule):
    '''
    Rule that sets the content on a stack object whenever content is available.
    '''

    def __init__(self, setter, index= -1):
        '''
        Construct the set rule.
        
        @param setter: callable(object, string)
            The callable used to set on the first object the received content (second entry).
        @param index: integer
            The index from which to take the stack object to set the content on.
        '''
        assert callable(setter), 'Invalid setter callable %s' % setter
        assert isinstance(index, int), 'Invalid index %s' % index
        self._setter = setter
        self._index = index

    def content(self, digester, content):
        '''
        @see: Rule.content
        '''
        self._setter(digester.stack[self._index], content)
