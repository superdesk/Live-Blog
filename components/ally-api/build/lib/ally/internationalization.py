'''
Created on May 26, 2011

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides internationalization support.
'''

# --------------------------------------------------------------------

def gettext(msg):
    '''
    Return the localized translation of message, based on the current global domain, language, and locale directory.
    This function is usually aliased as _() in the local namespace.
    
    @param msg: string
        The key message.
    @return: string
        The translated message.
    '''
    assert isinstance(msg, str), 'Invalid key message %s' % msg
    return msg

def _(msg):
    '''
    Alias function for @see: gettext.
    
    @param msg: string
        The key message.
    @return: string
        The translated message.
    '''
    return gettext(msg)

def ngettext(msg, msgp, count):
    '''
    Like @see: gettext, but consider plural forms. If a translation is found, apply the plural formula to n, and return
    the resulting message (some languages have more than two plural forms). If no translation is found, return singular
    if n is 1; return plural otherwise. The Plural formula is taken from the catalog header. It is a C or Python
    expression that has a free variable n; the expression evaluates to the index of the plural in the catalog.
    See the GNU gettext documentation for the precise syntax to be used in .po files and the formulas for a variety of
    languages.
    
    @param msg: string
        The key message.
    @param msgp: string
        The plural key message.
    @return: string
        The translated message.
    '''
    assert isinstance(msg, str), 'Invalid key message %s' % msg
    assert isinstance(msgp, str), 'Invalid plural key message %s' % msg
    if count == 1: return msg
    return msgp

def pgettext(ctxt, msg):
    '''
    Like @see: gettext, but use the provided context for the message.
    
    @param ctxt: string
        The context of the key message.
    @param msg: string
        The key message.
    @return: string
        The translated message.
    '''
    assert isinstance(ctxt, str), 'Invalid context %s' % ctxt
    return gettext(msg)

def C_(ctxt, msg):
    '''
    Alias method for @see: pgettext.
    
    @param ctxt: string
        The context of the key message.
    @param msg: string
        The key message.
    @return: string
        The translated message.
    '''
    return pgettext(ctxt, msg)

def npgettext(ctxt, msg, msgp, count):
    '''
    Like @see: ngettext, but use the provided context for the message.
    
    @param ctxt: string
        The context of the key message.
    @param msg: string
        The key message.
    @param msgp: string
        The plural key message.
    @return: string
        The translated message.
    '''
    assert isinstance(ctxt, str), 'Invalid context %s' % ctxt
    return ngettext(msg, msgp, count)

def N_(msg):
    '''
    Marking method that doesn't actually perform any translation it will just return the provided message key, it used
    in order to mark translatable message keys.
    
    @param msg: string
        The key message.
    @return: string
        The provided message key.
    '''
    assert isinstance(msg, str), 'Invalid key message %s' % msg
    return msg

def NC_(ctxt, msg):
    '''
    Like @see: N_, but use the provided context for the message.
    
    @param ctxt: string
        The context of the key message.
    @param msg: string
        The key message.
    @return: string
        The provided message key.
    '''
    assert isinstance(msg, str), 'Invalid key message %s' % msg
    return msg

# --------------------------------------------------------------------
