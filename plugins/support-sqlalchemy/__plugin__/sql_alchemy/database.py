'''
Created on Jan 8, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains sql alchemy database setup.
'''

from ally.container import ioc
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session, sessionmaker

# --------------------------------------------------------------------

@ioc.config
def database_url():
    '''The database URL, something like sqlite:///rest.db'''
    raise ioc.ConfigError('A database URL is required')

@ioc.config
def alchemy_pool_recycle(): '''The time to recycle pooled connection'''; return 3600

@ioc.config
def alchemy_create_tables(): '''Flag indicating that the table should be auto created'''; return True

@ioc.entity
def alchemySessionCreator() -> Session: return sessionmaker(bind=alchemyEngine())

@ioc.entity
def alchemyEngine() -> Engine:
    engine = create_engine(database_url(), pool_recycle=alchemy_pool_recycle())
    return engine

@ioc.entity
def metas(): return []

# ---------------------------------

@ioc.start
def createTables():
    if alchemy_create_tables():
        for meta in metas(): meta.create_all(alchemyEngine())
