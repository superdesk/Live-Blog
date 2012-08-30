'''
Created on Dec 20, 2011

@package: Superdesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Used for reading profiling statistics.
'''

import pstats

# --------------------------------------------------------------------

if __name__ == '__main__':
    p = pstats.Stats('output.stats')
    #p.sort_stats('time').print_stats(10)
    #p.sort_stats('cumulative').print_stats(10)
    p.sort_stats('time', 'cum').print_stats(.5, 'init')
