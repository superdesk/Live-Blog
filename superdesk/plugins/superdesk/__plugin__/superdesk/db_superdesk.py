'''
Created on Jan 17, 2012

@package: superdesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the database settings for the superdesk database.
'''

from ally.container import ioc, support
from ally.container.binder_op import bindValidations
from ally.support.sqlalchemy.mapper import mappingsOf
from ally.support.sqlalchemy.session import bindSession
from sql_alchemy import database_config
from sql_alchemy.database_config import alchemySessionCreator, metas, createTables
from superdesk.meta.metadata_superdesk import meta

# --------------------------------------------------------------------

support.include(database_config)

# --------------------------------------------------------------------

createTables = createTables
alchemySessionCreator = alchemySessionCreator

@ioc.replace(database_url)
def database_url():
    '''This database URL is used for the Superdesk tables'''
    return 'sqlite:///workspace/superdesk.db'

@ioc.replace(metas)
def metas(): return [meta]

def bindSuperdeskSession(proxy): bindSession(proxy, alchemySessionCreator())
def bindSuperdeskValidations(proxy): bindValidations(proxy, mappingsOf(meta))
