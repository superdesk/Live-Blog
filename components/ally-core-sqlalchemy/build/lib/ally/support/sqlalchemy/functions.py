'''
Created on May 19, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the SQL alchemy functions in a form that is more friendly for the API models.
'''

from sqlalchemy.sql import functions
from datetime import datetime

# --------------------------------------------------------------------

class current_timestamp(functions.current_timestamp, datetime):
    '''
    @see: functions.current_timestamp
    '''
    def __new__(cls): return datetime.now()
