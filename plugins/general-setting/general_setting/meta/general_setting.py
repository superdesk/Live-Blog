'''
Created on January 27, 2014

@package: general setting
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for general settings API.
'''

from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from superdesk.meta.metadata_superdesk import Base
from general_setting.api.general_setting import GeneralSetting

# --------------------------------------------------------------------

class GeneralSettingMapped(Base, GeneralSetting):
    '''
    Provides the mapping for PostType.
    '''
    __tablename__ = 'general_setting'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Key = Column('key', String(100), nullable=False, unique=True)
    Group = Column('group', String(100))
    Value = Column('value', String(100))
    # None REST model attribute --------------------------------------
    id = Column('id', INTEGER(unsigned=True), primary_key=True)
