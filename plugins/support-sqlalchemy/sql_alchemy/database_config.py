'''
Created on Jan 8, 2012

@package: support sqlalchemy
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains sql alchemy database setup.
'''

from ally.container import ioc, app
from ally.container.error import ConfigError
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import sessionmaker
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.config
def database_url():
    '''
    The database URL, something like:
        "sqlite:///{database}.db"
        "mysql+mysqlconnector://{user}:{password}@localhost/{database}"
    '''
    raise ConfigError('A database URL is required')

@ioc.config
def alchemy_pool_recycle():
    '''The time to recycle pooled connection'''
    return 3600

@ioc.entity
def alchemySessionCreator(): return sessionmaker(bind=alchemyEngine())

@ioc.entity
def alchemyEngine() -> Engine:
    return create_engine(database_url(), pool_recycle=alchemy_pool_recycle())

@ioc.entity
def metas(): return []

# --------------------------------------------------------------------

@app.populate(app.DEVEL, app.CHANGED, priority=app.PRIORITY_TOP)
def createTables():
    for meta in metas(): meta.create_all(alchemyEngine())
