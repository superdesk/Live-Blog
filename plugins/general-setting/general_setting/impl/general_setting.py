'''
Created on January 27, 2014

@package: general setting
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for the configuration API.
'''


from ally.container.ioc import injected
from ally.container.support import setup
from general_setting.api.general_setting import IGeneralSettingService,\
    QGeneralSetting
from general_setting.meta.general_setting import GeneralSettingMapped
from sql_alchemy.impl.keyed import EntityServiceAlchemy

# --------------------------------------------------------------------

@injected
@setup(IGeneralSettingService, name='generalSettingService')
class GeneralSettingAlchemy(EntityServiceAlchemy, IGeneralSettingService):
    '''
    @see: IGeneralSettingService
    '''
    def __init__(self):
        EntityServiceAlchemy.__init__(self, GeneralSettingMapped, QGeneralSetting)