'''
Created on Jan 15, 2014

@package: workflow
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

AAP Workflow testing.

'''
# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

import logging
import unittest

from ally.design.processor.context import Context
from ally.design.processor.assembly import Assembly
from ally.container.ioc import initialize
from ally.design.processor.execution import Processing, FILL_ALL
from ally.support.util_context import listBFS
from workflow.core.impl.processor.desk import DeskHandler

#---------------------------------------------------------------

logging.basicConfig()
logging.getLogger('ally.design.processor').setLevel(logging.INFO)

#-------------------------------------------------------------------
class TestGraphStructure(unittest.TestCase):
    
    def testGraph(self):
        deskHandler = DeskHandler()
        
        assemblyWorkflow = Assembly('Build Desk Workflow')
        assemblyWorkflow.add(initialize(deskHandler))
        #assemblyWorkflow.add(initialize(workflowHandler))
        
        proc = assemblyWorkflow.create()
        assert isinstance(proc, Processing)
        
        arg = proc.execute(FILL_ALL)
        arg.solicit.nodes
    
    
    
    
    