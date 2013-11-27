'''
Created on Nov 7, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Contains the services for content plugins.
'''

from ally.container import support, bind, ioc
from content.base.api.item import IItemService
from content.base.core.spec import IItemHandler
from content.base.impl.item import ItemHandlersSetup

from ..plugin.registry import registerService
from .database import binders
from ally.cdm.impl.local_filesystem import IDelivery, HTTPDelivery,\
    LocalFileSystemCDM
from __plugin__.cdm.service import server_uri, repository_path
from ally.cdm.spec import ICDM
from ally.cdm.support import ExtendPathCDM
from content.resource.core.spec import IReader
from ally.design.processor.handler import Handler
from content.resource.core.parse.impl.processor.parser_html_handler import ParserHTMLHandler
from content.resource.core.parse.impl.processor.formatting_process_handler import FormattingProcessorHandler
from ally.design.processor.assembly import Assembly


# --------------------------------------------------------------------
SERVICES = 'content.*.api.**.I*Service'

bind.bindToEntities('content.*.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('content.*.impl.**.*')
support.listenToEntities(SERVICES, listeners=registerService)
support.loadAllEntities(SERVICES)

# --------------------------------------------------------------------

bind.bindToEntities('content.*.core.impl.**.*Alchemy', binders=binders)
support.createEntitySetup('content.*.core.impl.**.*')

# --------------------------------------------------------------------

@ioc.entity
def itemHandlers() -> list: return support.entitiesFor(IItemHandler)

@ioc.entity
def itemBase() -> IItemService:
    return support.entityFor(ItemHandlersSetup).createService()

@ioc.entity
def delivery() -> IDelivery:
    d = HTTPDelivery()
    d.serverURI = server_uri()
    d.repositoryPath = repository_path()
    return d

@ioc.entity
def contentDeliveryManager() -> ICDM:
    cdm = LocalFileSystemCDM();
    cdm.delivery = delivery()
    return cdm

@ioc.entity
def cdmItem() -> ICDM:
    '''
    The content delivery manager (CDM) for the items content.
    '''
    return ExtendPathCDM(contentDeliveryManager(), 'item/%s')

@ioc.entity
def contentReaders() -> dict:
    readersList = support.entitiesFor(IReader)
    readers = dict()
    for reader in readersList:
        assert isinstance(reader, IReader), 'Invalid reader %s' % reader
        reader.register(readers)
    return readers

# --------------------------------------------------------------------

@ioc.entity
def assemblyParseContent() -> Assembly:
    '''
    The assembly containing the parsers for text content.
    '''
    return Assembly('Parse text content')

@ioc.entity
def parserHTMLProvider() -> Handler: return ParserHTMLHandler()

@ioc.entity
def formattingProcessorProvider() -> Handler: return FormattingProcessorHandler()

@ioc.before(assemblyParseContent)
def updateAssemblyParseContent():
    assemblyParseContent().add(parserHTMLProvider(), formattingProcessorProvider())
