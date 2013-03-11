'''
Created on Mar 11, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API implementation for content.
'''

from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from content.packager.api.reference import IReferenceService, Reference
from ally.api.config import call

# --------------------------------------------------------------------

@setup(IReferenceService, name='referenceService')
class ReferenceServiceAlchemy(EntityServiceAlchemy, IReferenceService):
    '''
    Implementation for @see: IReferenceService
    '''

    @call
    def getById(self, idref:Reference.Idref) -> Reference:
        '''
        Provides the item based on the id.

        @param idref: string
            The id of the entity to find.
        @raise InputError: If the id is not valid.
        '''
