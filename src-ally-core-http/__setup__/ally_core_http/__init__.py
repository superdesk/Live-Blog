'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains setup and configuration files for the REST server.
'''

from ally import ioc

# --------------------------------------------------------------------
# The default configurations

ioc.configurations({
                    'applicationMode':'devel',
                    'serverType':'basic',
                    'ajaxCrossDomain':False,
                    'phpZendSupport':False,
                    })
