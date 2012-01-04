'''
Created on Jul 15, 2011

@package Newscoop
@copyright 2011 Sourcefabric o.p.s.
@license http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains setup and configuration files for the plugins support.
'''

from ally import ioc, aop

# --------------------------------------------------------------------

@ioc.start
def load():
    ioc.deploy(aop.modulesIn('__plugin__.*', '__plugin__.*.*'))
