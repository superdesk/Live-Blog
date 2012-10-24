'''
Created on Oct 18, 2012

@package support sqlalchemy
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains pool implementations for sql alchemy database setup.
'''

from multiprocessing.process import current_process
from sqlalchemy.pool import Pool

# --------------------------------------------------------------------

class SingletonProcessWrapper(Pool):
    '''
    Class made based on @see: sqlalchemy.pool.Pool, only implements the public methods.
    
    A Pool that wraps another pool that will be recreated for each process.

    Maintains one pool per each process, never moving a connection pool to a process other than the one which it
    was created in.
    '''

    def __init__(self, wrapped):
        assert isinstance(wrapped, Pool), 'Invalid wrapped pool %s' % wrapped
        
        self._wrapped = wrapped
        self._pools = set()

    def unique_connection(self):
        '''
        @see: Pool.unique_connection
        '''
        return self._getPool().unique_connection()
    
    def connect(self):
        '''
        @see: Pool.connect
        '''
        return self._getPool().connect()

    def recreate(self):
        '''
        @see: Pool.recreate
        '''
        return SingletonProcessWrapper(self._wrapped)

    def dispose(self):
        '''
        @see: Pool.dispose
        '''
        for pool in self._pools: pool.dispose()
        self._pools.clear()

    def status(self):
        '''
        @see: Pool.status
        '''
        return "SingletonProcessWrapper id:%d size: %d" % (id(self), len(self._pools))
    
    def _getPool(self):
        '''
        Provides the pool for the current process.
        '''
        process = current_process()
        try: return process._ally_db_pool
        except AttributeError: pass
        pool = process._ally_db_pool = self._wrapped.recreate()
        self._pools.add(pool)
        return pool
