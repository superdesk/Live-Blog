from ally.api.config import service
from ally.support.api.entity import Entity, IEntityGetService
from ally.api.config import model

@model
class Mock(Entity):
    '''
    
    '''

@service((Entity, Mock))
class IMockService(IEntityGetService):
    '''
    '''
    