'''
Created on Oct 18, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Configuration to add multiprocessing abilities to the database.
'''

from ally.container import support

# --------------------------------------------------------------------

try:
    from sqlalchemy.engine.base import Engine
    from ally.core.sqlalchemy.pool import SingletonProcessWrapper
except ImportError:
    # Probably there is no sql alchemy available.
    pass
else:
    def present(engine):
        '''
        Used for listening to all sql alchemy engines that are created in order to wrap the engine pool with a pool that can
        handle multiple processors.
        '''
        if not isinstance(engine.pool, SingletonProcessWrapper):
            engine.pool = SingletonProcessWrapper(engine.pool)
    
    support.listenToEntities(Engine, listeners=present, module=support.ALL)
