'''
Created on Dec 13, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Module containing the nodes for the IoC wiring setup.
'''

from .node import Source, Initializer
from inspect import isclass
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Creator(Source):
    '''
    Creates entities for a class.
    '''
    
    def __init__(self, name, clazz):
        '''
        @see: Source.__init__
        
        @param clazz: class
            The class 
        '''
        Source.__init__(self, name, clazz)
        assert isclass(clazz), 'Invalid class %s' % clazz
        self._clazz = clazz
        
    def _process(self):
        '''
        Processes the function value.
        @see: Source.processValue
        '''
        entity = self._clazz()
        self.doSetValue(self._path, entity)
        self._listenersBefore()
        log.debug('Created and set entity %s of node %s', entity, self)
        
        Initializer.initialize(entity)
        self._listenersAfter()
        log.debug('Initialized and set entity %s of node %s', entity, self)
        return entity
