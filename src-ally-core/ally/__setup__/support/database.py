'''
Created on Jul 26, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configuration for the database.
'''

from ally import ioc
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import sessionmaker

# --------------------------------------------------------------------

alchemySessionCreator = lambda alchemyEngine: sessionmaker(bind=alchemyEngine)

def alchemyEngine(_databaseURL:'Something like sqlite:///rest.db',
                  _alchemyPoolRecycle:'The time to recycle pooled connection'=3600) -> Engine:
    engine = create_engine(_databaseURL, pool_recycle=_alchemyPoolRecycle)
    return engine

# ---------------------------------

@ioc.after('services')
def createTables(ctx, alchemyEngine, metas=[],
                 _alchemyCreateTables:'Flag indicating that the table should be auto created'=True):
    if _alchemyCreateTables:
        for meta in metas: meta.create_all(alchemyEngine)
