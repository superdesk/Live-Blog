'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The core of ally py framework for REST.
'''
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.config
def use_old_encdec():
    '''
    Temporary flag that allows the use of the old encoders and decoders, this are kept for compatibility purposes with
    the old applications.
    '''
    return False
