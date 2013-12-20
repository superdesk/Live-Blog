'''
Created on Dec 19, 2013

@package: gui core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Livedesk XML Digester rules.

'''
from ally.xml.digester import Rule
from ally.support.util_context import IPrepare
from ally.design.processor.context import Context
from ally.design.processor.attribute import defines
from ally.xml.context import DigesterArg
from ally.design.processor.resolvers import merge

# --------------------------------------------------------------------

class CollaboratorTypeRule(Rule, IPrepare):
    '''
    Digester rule for extracting UserType actions from the xml livedesk-config file.
    '''
    class Repository(Context):
        '''
        The UserType context.
        '''
        # ---------------------------------------------------------------- Defined
        userType = defines(str, doc='''
        @rtype: string
        The user type.
        ''')
        actions = defines(list, doc='''
        @rtype: list[Context]
        The list of actions for the UserType.
        ''')
        children = defines(list, doc='''
        @rtype: list[Context]
        ''')
    
    def prepare(self, resolvers):
        '''
        @see: IVerifier.prepare
        '''
        merge(resolvers, dict(Repository=self.Repository))
    
    def begin(self, digester, **attributes):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        repository = digester.arg.Repository()
        assert isinstance(repository, CollaboratorTypeRule.Repository), 'Invalid repository %s' % repository
        
        repository.userType = attributes.get('name')
        repository.actions = []
        digester.stack.append(repository)
    
    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        assert digester.stack, 'Expected a repository on the digester stack'
        userType = digester.stack.pop()
        assert isinstance(userType, self.Repository), 'Invalid repository %s' % userType
        repository = digester.stack[-1]
        assert isinstance(repository, self.Repository), 'Invalid repository %s' % repository
        
        if repository.children is None: repository.children = []
        repository.children.append(userType)
    
    