'''
Created on April 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for liveblog sync.
'''

import abc

# --------------------------------------------------------------------

class IBlogSync(metaclass=abc.ABCMeta):
    '''
    The blog sync specification.
    '''

    @abc.abstractclassmethod
    def syncBlogs(self):
        '''
        Sync the blogs on automatic publishing.
        '''
