'''
Created on May 27, 2013

@package: superdesk user
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

Populates default data for the services.
'''

from ally.container import app, ioc
from ally.container.support import entityFor
from superdesk.user.api.user_type import IUserTypeService, UserType
from ally.design.priority import PRIORITY_FIRST

# --------------------------------------------------------------------

@ioc.config
def standard_user_types():
    ''' The standard user types '''
    return ['standard']

@app.populate(app.DEVEL, priority=PRIORITY_FIRST)
def populateTypes():
    userTypeService = entityFor(IUserTypeService)
    assert isinstance(userTypeService, IUserTypeService)
    for key in standard_user_types():
        utype = UserType()
        utype.Key = key
        try: userTypeService.insert(utype)
        except: pass
