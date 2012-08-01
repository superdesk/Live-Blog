'''
Created on Aug 25, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for article type.
'''

from .entity import Entity, IEntityService
from ally.api.config import model, service

# --------------------------------------------------------------------

@model
class ArticleType(Entity):
    '''
    Provides the article type model.
    '''
    Name = str

# --------------------------------------------------------------------

@service((Entity, ArticleType))
class IArticleTypeService(IEntityService):
    '''
    Provides services for article types.
    '''
