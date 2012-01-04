'''
Created on May 26, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides internationalization support.
'''

import re
from .type_legacy import Number, Iterable, Callable

# --------------------------------------------------------------------

# The prefix that is used for marking the place holders
MARK_PLACE_HOLDER = '$'
MARK_PLACE_LENGHT = len(MARK_PLACE_HOLDER)

# The pattern used for split the parameter calls.
REGEX_ID = re.compile('[1-9][0-9]*')

# --------------------------------------------------------------------

class Internationalizator(Callable):
    '''
    Class that provides the support for internationalization.
    '''
    
    def __init__(self, name):
        '''
        @param name: string
            The name of the assigned to the internationalization.
        '''
        assert isinstance(name, str) and len(name) > 0, 'Invalid name %s' % name
        self.name = name
        
    def __call__(self, msg, *args):
        '''
        Called in order to create a translated message.
        
        @param msg: string
            The message (that is in English) to be used as a key, this message
            has to contain as many place holders (ex: $1, $2 ...) as there are 
            arguments.
        @param *args: arguments
            The arguments to be used instead of the place holders in the message.
        '''
        return TRANSLATOR.translate(self.name, msg, args)
        
# --------------------------------------------------------------------

def translator(name):
    '''
    Creates an internationalizator for the provided name.
    
    @param name: string
        This is usually the module name in which the translations occur.
    '''
    return Internationalizator(name)

# --------------------------------------------------------------------

class Translator:
    '''
    Provides the translation of messages.
    '''
    
    def translate(self, name, msg, args):
        '''
        Provides the translation for the default message, this class should be extended by the translators.
        
        @param name: string
            The name for the group of the translation messages (usually the module name).
        @param msg: string
            The message (that is in English) to be used as a key, this message
            has to contain as many place holders (ex: $1, $2 ...) as there are 
            arguments.
        @param args: list[object]
            The arguments to be used instead of the place holders in the message.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(msg, str), 'The msg (message key) needs to be a string'
        assert isinstance(args, Iterable), 'Invalid arguments, are not iterable %s' % args
        if __debug__:
            for arg in args:
                assert isinstance(arg, (str, Number)), \
                'The arguments can be only of string and number types, received %r' % arg
                
        compiled = []
        search, index = True, 0
        while search:
            k = msg.find(MARK_PLACE_HOLDER, index)
            if k > index:
                idGr = REGEX_ID.search(msg, k + MARK_PLACE_LENGHT)
                if idGr is None:
                    raise AssertionError('Could not locate any valid id at index %s' % (k + MARK_PLACE_LENGHT))
                
                id = int(idGr.group(0)) - 1
                compiled.append(msg[index:k])
                try:
                    compiled.append(str(args[id]))
                except IndexError:
                    raise AssertionError('Could not locate a parameter for id %s' % (MARK_PLACE_HOLDER + 
                                                                                     str(id + 1)))
                
                index = idGr.end(0)
            else:
                search = False
                
        if index < len(msg):
            compiled.append(msg[index:])
            
        return ''.join(compiled)

# --------------------------------------------------------------------

TRANSLATOR = Translator()
# The translator used by all internationalization, change this in order to have another translator support.
