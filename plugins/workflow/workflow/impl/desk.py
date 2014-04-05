'''
Created on Jan 9, 2014

@package: workflow
@copyright: 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Implementation for desk service.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from sql_alchemy.impl.entity import EntityServiceAlchemy
from ..api.desk import IDeskService, QDesk
from ..meta.desk import DeskMapped, DeskDesk
from ally.api.validate import validate
from sql_alchemy.support.util_service import iterateCollection
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import aliased

# --------------------------------------------------------------------

DeskSource = aliased(DeskMapped)
DeskDestination = aliased(DeskMapped)
DeskDeskSource = aliased(DeskDesk)

# --------------------------------------------------------------------

@injected
@setup(IDeskService, name='deskService')
@validate(DeskMapped)
class DeskServiceAlchemy(EntityServiceAlchemy, IDeskService):
    '''
    Implementation for @see: IDeskService
    '''
    def __init__(self):
        EntityServiceAlchemy.__init__(self, DeskMapped, QDesk)

    def getDestinations(self, name, q=None, **options):
        '''
        @see IDeskService.getDestinations 
        '''
        #first get the id of the node
        try: sourceId, = self.session().query(DeskMapped.id).filter(DeskMapped.Name == name).one()
        except NoResultFound: return None
        
        sql = self.session().query(DeskMapped.Name).join(DeskDesk, DeskDesk.destination == DeskMapped.id)
        sql = sql.filter(DeskDesk.source == sourceId)
        return iterateCollection(sql)
    
    def addDestination(self, fromDesk, toDesk):
        '''
        @see IDeskService.addDestination 
        '''
        #first make sure the two nodes exist
        try:
            source, = self.session().query(DeskMapped.id).filter(DeskMapped.Name == fromDesk).one()
            destination, = self.session().query(DeskMapped.id).filter(DeskMapped.Name == toDesk).one()
        except NoResultFound: return False
        
        #look for existing connection between the two
        sql = self.session().query(DeskDesk).join(DeskSource, DeskSource.id == DeskDesk.source)
        sql = sql.join(DeskDestination, DeskDestination.id == DeskDesk.destination)
        sql = sql.filter((DeskSource.Name == fromDesk) & (DeskDestination.Name == toDesk))
        
        #if no connection, create one
        if sql.count() == 0:
            connection = DeskDesk()
            connection.source = source
            connection.destination = destination
            self.session().add(connection)
            return True
        return False
    
    def remDestination(self, fromDesk, toDesk):
        '''
        @see IDeskService.remDestination 
        '''
        sql = self.session().query(DeskDesk).join(DeskSource, DeskSource.id == DeskDesk.source)
        sql = sql.join(DeskDestination, DeskDestination.id == DeskDesk.destination)
        sql = sql.filter((DeskSource.Name == fromDesk) & (DeskDestination.Name == toDesk))
        
        try: deskDesk = sql.one()
        except NoResultFound: return False
        self.session().delete(deskDesk)
        return True
