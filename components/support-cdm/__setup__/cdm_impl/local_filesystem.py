'''
Created on Jan 5, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides the configurations for the CDM local filesystem implementation.
'''

from cdm.spec import ICDM
from cdm.impl.local_filesystem import LocalFileSystemCDM
from ally.container import ioc

# --------------------------------------------------------------------
# Creating the content delivery managers

@ioc.entity
def localFileSystemCDM() -> ICDM:
    b = LocalFileSystemCDM();
    b.repositoryPath = ''
    return b

# ---------------------------------

@ioc.entity
def cdms():
    return [localFileSystemCDM()]
