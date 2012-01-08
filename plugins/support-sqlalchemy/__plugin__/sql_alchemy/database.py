'''
Created on Jan 8, 2012

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains sql alchemy database setup.
'''

from ally.container import ioc
from ally.container.ioc import SetupError
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session, sessionmaker

# --------------------------------------------------------------------

@ioc.config
def databaseURL():
    '''The database URL, something like sqlite:///rest.db'''
    raise SetupError('A database URL is required')

@ioc.config
def alchemyPoolRecycle(): '''The time to recycle pooled connection'''; return 3600

@ioc.config
def alchemyCreateTables(): '''Flag indicating that the table should be auto created'''; return True

@ioc.entity
def alchemySessionCreator() -> Session: return sessionmaker(bind=alchemyEngine())

@ioc.entity
def alchemyEngine() -> Engine:
    engine = create_engine(databaseURL(), pool_recycle=alchemyPoolRecycle())
    return engine

@ioc.entity
def metas(): return []

# ---------------------------------

@ioc.start
def createTables():
    if alchemyCreateTables():
        for meta in metas(): meta.create_all(alchemyEngine())
