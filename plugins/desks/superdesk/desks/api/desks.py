from ally.api.config import service
from ally.support.api.entity import Entity, IEntityGetService
from ally.api.config import model

@model
class Desk(Entity):
    '''
    
    '''

@service((Entity, Desk))
class IDesksService(IEntityGetService):
    '''
    '''
    