'''
Created on January 27, 2014

@package: general setting
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Provides general setting API.
'''

from ally.api.config import service, model, query
from ally.api.criteria import AsLikeOrdered
from ally.support.api.keyed import Entity, QEntity

# --------------------------------------------------------------------

@model
class GeneralSetting(Entity):
    '''
    Provides the configuration model.
    '''
    Key = str
    Group = str
    Value = str

# --------------------------------------------------------------------

@query(GeneralSetting)
class QGeneralSetting(QEntity):
    '''
    Provides the query for the general setting model.
    '''
    key = AsLikeOrdered
    group = AsLikeOrdered

# --------------------------------------------------------------------

@service((Entity, GeneralSetting), (QEntity, QGeneralSetting))
class IGeneralSettingService:
    '''
    Provides the general setting service.
    '''
    
