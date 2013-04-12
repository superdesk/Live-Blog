'''
Created on Nov 7, 2012

@package: ally plugin
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Update the default logging.
'''

from ..ally.logging import info_for
from .distribution import application_mode, APP_DEVEL
from ally.container import ioc
from ally.design import processor
import logging

# --------------------------------------------------------------------

@ioc.before(info_for)
def updateInfos():
    info_for().append('__plugin__')

# --------------------------------------------------------------------

@ioc.start(priority=ioc.PRIORITY_TOP)
def updateDevelopment():
    if application_mode() == APP_DEVEL:
        logging.getLogger(processor.__name__).setLevel(logging.INFO)
