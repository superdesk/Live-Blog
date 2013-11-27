'''
Created on Nov 22, 2013

@package: content
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Defines context used by the parser processor.
'''

from ally.design.processor.context import Context
from ally.design.processor.attribute import defines, requires
from ally.api.model import Content

# --------------------------------------------------------------------

class Parser(Context):
    '''
    Context used by the content parser processors. 
    '''
    # ---------------------------------------------------------------- Defined
    preFormatting = defines(dict, doc='''
    @rtype: dict
    Dictionary of index:formatting tag pairs identifying formatting tags in the
    original content.
    ''')
    # ---------------------------------------------------------------- Required
    content = requires(Content, doc='''
    The content to be parsed.
    ''')
