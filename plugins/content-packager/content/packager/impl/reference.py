'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for reference.
'''

from ally.container.support import setup
from content.packager.api.reference import IReferenceService, QReference
from sql_alchemy.impl.entity import EntitySupportAlchemy
from ally.exception import InputError, Ref
from content.packager.meta.reference import ReferenceMapped
from ally.api.extension import IterPart

# --------------------------------------------------------------------

@setup(IReferenceService, name='referenceService')
class ReferenceServiceAlchemy(EntitySupportAlchemy, IReferenceService):
    '''
    Implementation for @see: IReferenceService
    '''

    def __init__(self):
        '''
        Construct the reference service.
        '''
        EntitySupportAlchemy.__init__(self, ReferenceMapped, QReference)

    def getById(self, idref):
        '''
        Implementation for @see: IReferenceService.getById
        '''
        reference = self.session().query(ReferenceMapped).get(idref)
        if not reference: raise InputError(Ref(_('Unknown id'), ref=ReferenceMapped.Idref))
        return reference

    def getAll(self, offset, limit, detailed, q):
        '''
        Implementation for @see: IReferenceService.getAll
        '''
        if detailed:
            references, total = self._getAllWithCount(None, q, offset, limit)
            return IterPart(references, total, offset, limit)
        return self._getAll(None, q, offset, limit)
