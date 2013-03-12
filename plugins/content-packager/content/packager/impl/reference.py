'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for reference.
'''

from ally.container.support import setup
from content.packager.api.reference import IReferenceService, Reference

# --------------------------------------------------------------------

@setup(IReferenceService, name='referenceService')
class ReferenceServiceAlchemy(IReferenceService):
    '''
    Implementation for @see: IReferenceService
    '''

    def getById(self, idref):
        '''
        Implementation for @see: IReferenceService.getById
        '''
        ref = Reference()
        return ref

    def getAll(self, offset, limit, detailed, q):
        '''
        Implementation for @see: IReferenceService.getAll
        '''
        return []
