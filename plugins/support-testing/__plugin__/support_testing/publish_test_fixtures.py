'''
Created on April 1, 2014

@package: support testing
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the publish of tests fixtures files.
'''

import os
import logging
from ally.cdm.spec import ICDM
from __plugin__.cdm import contentDeliveryManager
from __plugin__.gui_core.gui_core import publish
from ally.container import ioc

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def getTestFixturePath(file=None):
    '''Provides the file path within the plugin "test_fixtures" directory'''
    modulePath = os.path.realpath(__file__)
    for _k in range(0, __name__.count('.') + 1):
        modulePath = os.path.dirname(modulePath)
    path = os.path.join(modulePath, 'test_fixtures')
    if file: path = os.path.join(path, file.replace('/', os.sep))
    return path

@ioc.entity
def cdmTestFixtures() -> ICDM:
    '''
    The content delivery manager (CDM) for the plugin's static resources
    '''
    return contentDeliveryManager()

@ioc.config
def test_fixtures_folder():
    '''Describes where the test fixtures files are published '''
    return 'tests'

@publish
def publishTestFixtures():
    '''
    Publishes tests fixtures
    '''
    log.info('Published text fixtures from \'%s\' to \'%s\'', getTestFixturePath(), test_fixtures_folder())
    cdmTestFixtures().publishFromDir(test_fixtures_folder(), getTestFixturePath())

# --------------------------------------------------------------------