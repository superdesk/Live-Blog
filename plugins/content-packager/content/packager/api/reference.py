'''
Created on Mar 8, 2013

@package: content packager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

API specifications for reference.
'''

from content.packager.api.domain_content import modelContent
from ally.api.config import query, service, call, LIMIT_DEFAULT
from ally.api.criteria import AsLike, AsRangeOrdered
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelContent(id='Idref')
class Reference:
    '''
    Provides the reference model.
    '''
    Idref = str
    ItemClass = str
    ResidRef = str
    Href = str
    Size = int
    Rendition = str
    ContentType = str
    Format = str

# --------------------------------------------------------------------

@query(Reference)
class QReference:
    '''
    Provides the reference query.
    '''
    itemClass = AsLike
    size = AsRangeOrdered
    rendition = AsLike
    contentType = AsLike
    format = AsLike

# --------------------------------------------------------------------

@service
class IReferenceService:
    '''
    Provides the service methods for Reference model.
    '''

    @call
    def getById(self, idref:Reference.Idref) -> Reference:
        '''
        Provides the reference based on the id.

        @param idref: string
            The id of the reference to find.
        @raise InputError: If the id is not valid.
        '''

    @call
    def getAll(self, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True, q:QReference=None) -> Iter(Reference):
        '''
        Provides the references searched by the provided query.

        @param offset: integer
            The offset to retrieve the entities from.
        @param limit: integer
            The limit of entities to retrieve.
        @param detailed: boolean
            If true will present the total count, limit and offset for the partially returned collection.
        @param q: QReference
            The query to search by.
        '''

    @call
    def insert(self, reference:Reference) -> Reference.Idref:
        '''
        Insert the reference, also the reference will have automatically assigned the Id to it.

        @param reference: Reference
            The reference to be inserted.

        @return: The id assigned to the reference
        @raise InputError: If the reference is not valid.
        '''

    @call
    def update(self, reference:Reference):
        '''
        Update the reference.

        @param reference: Reference
            The reference to be updated.
        '''

    @call
    def delete(self, id:Reference.Idref) -> bool:
        '''
        Delete the reference for the provided id.

        @param id: integer
            The id of the reference to be deleted.

        @return: True if the delete is successful, false otherwise.
        '''
