'''
Created on Dec 19, 2013

@package: gui core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Contains the Livedesk configuration service.
'''

from ally.container import ioc, support
from ally.design.processor.assembly import Assembly
from __setup__.ally.notifier import registersListeners
from ally.xml.digester import Node, RuleRoot
from ally.design.processor.handler import Handler
from ally.xml.parser import ParserHandler
from ally.notifier.impl.processor.configuration_notifier import ConfigurationListeners
from livedesk.impl.rules import CollaboratorTypeRule
from ally.xml.rules import ActionRule
from __plugin__.gui_core.service import uriRepositoryCaching, synchronizeAction

# --------------------------------------------------------------------
# The synchronization processors
syncCollaboratorType = syncCollaboratorActions = support.notCreated  # Just to avoid errors
support.createEntitySetup('livedesk.impl.processor.synchronize.**.*')

#-------------------------------------------------------------------------

@ioc.config
def livedesk_configuration():
    ''' The URI path where the XML Livedesk configuration is found.'''
    return ['file://../ui/livedesk/config-livedesk.xml']

# --------------------------------------------------------------------

@ioc.entity
def assemblyLivedeskConfiguration() -> Assembly:
    return Assembly('Livedesk Configurations')

@ioc.entity
def nodeRootXML() -> Node: return RuleRoot()

@ioc.entity
def parserXML() -> Handler:
    b = ParserHandler()
    b.rootNode = nodeRootXML()
    return b

@ioc.entity
def configurationLiveDeskListener() -> Handler:
    configLivedesk = ConfigurationListeners()
    configLivedesk.assemblyConfiguration = assemblyLivedeskConfiguration()
    configLivedesk.patterns = livedesk_configuration()
    return configLivedesk

# --------------------------------------------------------------------

@ioc.before(nodeRootXML)
def updateRootNodeXMLForCollaboratorType():
    nodeRootXML().addRule(CollaboratorTypeRule(), 'Livedesk/CollaboratorType')
    nodeRootXML().addRule(ActionRule(), 'Livedesk/CollaboratorType/Action')

@ioc.before(assemblyLivedeskConfiguration)
def updateAssemblyConfiguration():
    assemblyLivedeskConfiguration().add(parserXML(), uriRepositoryCaching(), synchronizeAction(), 
                                        syncCollaboratorType(), syncCollaboratorActions())

@ioc.before(registersListeners)
def updateRegistersListenersForConfiguration():
    registersListeners().append(configurationLiveDeskListener())
