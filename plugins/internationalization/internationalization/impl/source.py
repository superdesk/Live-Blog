'''
Created on Mar 5, 2012

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Implementation for the source API.
'''

from ..api.source import ISourceService, QSource
from ..meta.source import Source
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ally.container.ioc import injected
from ally.container.support import setup

# --------------------------------------------------------------------

@injected
@setup(ISourceService)
class SourceServiceAlchemy(EntityServiceAlchemy, ISourceService):
    '''
    Alchemy implementation for @see: ISourceService
    '''

    def __init__(self):
        EntityServiceAlchemy.__init__(self, Source, QSource)
