'''
Created on Dec 20, 2011

@package: Superdesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Used for reading profiling statistics.
'''

import pstats
import os

# --------------------------------------------------------------------

if __name__ == '__main__':
    # First we need to set the working directory relative to the application deployer just in case the application is
    # started from somewhere else
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    p = pstats.Stats('profile.data')
    # p.sort_stats('time').print_stats(10)
    #p.sort_stats('time').print_stats()
    p.sort_stats('time').print_stats(.5)
