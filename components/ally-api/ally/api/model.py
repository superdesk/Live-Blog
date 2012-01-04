'''
Created on Jun 16, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides special models that are interpreted by the core in specific ways.
'''

from .type import typeFor, TypeClass

# --------------------------------------------------------------------

class Content:
    '''
    Provides a container for content streaming.
    '''
    
typeFor(Content, TypeClass(Content, False))
