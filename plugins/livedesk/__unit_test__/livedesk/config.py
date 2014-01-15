'''
Created on Dec 19, 2013

@package: livedesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Livedesk configuration XML testing.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

import logging
import unittest
from ally.design.processor.context import Context
from ally.support.util_io import IInputStream
from ally.design.processor.attribute import defines, requires
from ally.xml.parser import ParserHandler
from ally.xml.digester import RuleRoot
from ally.design.processor.assembly import Assembly
from ally.container.ioc import initialize
from ally.design.processor.execution import Processing, FILL_ALL
from pkg_resources import get_provider, ResourceManager
from livedesk.impl.rules import CollaboratorTypeRule
from ally.xml.rules import ActionRule
from ally.support.util_context import listBFS

#---------------------------------------------------------------

logging.basicConfig()
logging.getLogger('ally.design.processor').setLevel(logging.INFO)

#-------------------------------------------------------------------

class TestSolicit(Context):
    '''
    The solicit context.
    '''
    # ---------------------------------------------------------------- Defined
    stream = defines(IInputStream)
    uri = defines(str)
    # ---------------------------------------------------------------- Required
    repository = requires(Context)

class TestConfigurationParsing(unittest.TestCase):
    
    def __init__(self, methodName):
        super().__init__(methodName)

    def testConfigParsing(self):
        parser = ParserHandler()
        parser.rootNode = RuleRoot()
        
        userTypeNode = parser.rootNode.addRule(CollaboratorTypeRule(), 'Livedesk/CollaboratorType')
        parser.rootNode.addRule(ActionRule(), 'Livedesk/CollaboratorType/Action')
        
        #prepare Assembly
        assemblyParsing = Assembly('Parsing XML')
        assemblyParsing.add(initialize(parser))
        
        parseResult = self.executeProcess(assemblyParsing)
        
        userTypes = listBFS(parseResult.solicit.repository, CollaboratorTypeRule.Repository.children, 
                            CollaboratorTypeRule.Repository.userType)
        userTypes
    
    def executeProcess(self, assembly):
        proc = assembly.create(solicit=TestSolicit)
        assert isinstance(proc, Processing)
        
        #use packageProvider (not os package) to access files from inside the package (like config_test.xml)
        packageProvider = get_provider(__name__)
        manager = ResourceManager()
        self.assertTrue(packageProvider.has_resource('config-livedesk.xml'), 'Livedesk Xml Config file missing')
        
        content = packageProvider.get_resource_stream(manager, 'config-livedesk.xml')
        solicit = proc.ctx.solicit(stream=content, uri = 'file://%s' % 'config-livedesk.xml')
        
        arg = proc.execute(FILL_ALL, solicit=solicit)
        assert isinstance(arg.solicit, TestSolicit)
        content.close()
        return arg
    
if __name__ == '__main__': unittest.main()

