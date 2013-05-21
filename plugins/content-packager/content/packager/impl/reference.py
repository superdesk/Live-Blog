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
from content.packager.meta.reference import ReferenceMapped
import logging
from sql_alchemy.impl.entity import EntityServiceAlchemy

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@setup(IReferenceService, name='referenceService')
class ReferenceServiceAlchemy(EntityServiceAlchemy, IReferenceService):
    '''
    Implementation for @see: IReferenceService
    '''

    def __init__(self):
        '''
        Construct the reference service.
        '''
        EntityServiceAlchemy.__init__(self, ReferenceMapped, QReference)
