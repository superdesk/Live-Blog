'''
Created on May 26, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides internationalization support.
'''

import gettext as pygettext

# --------------------------------------------------------------------

def textlocale(locale=None):
    '''
    Change or query the current global locale. If locale is None, then the current global locale is returned, otherwise
    the global locale is set to locale, which is returned.
    
    @param locale: string|None
        The locale to set, if None will return the current locale.
    @return: string|None
        None if the locale has been set, otherwise the current locale.
    '''
    assert locale is None or isinstance(locale, str), 'Invalid locale %s' % locale

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

def textdomain(domain=None):
    '''
    Change or query the current global domain. If domain is None, then the current global domain is returned, otherwise
    the global domain is set to domain, which is returned.
    
    @param domain: string|None
        The domain to set, if None will return the current domain.
    @return: string|None
        None if the domain has been set, otherwise the current domain.
    '''
    assert domain is None or isinstance(domain, str), 'Invalid domain %s' % domain
    return pygettext.textdomain(domain)

def dgettext(domain, msg):
    '''
    Like @see: gettext, but look the message up in the specified domain.
    
    @param domain: string
        The domain of the key message.
    @param msg: string
        The key message.
    @return: string
        The translated message.
    '''
    assert isinstance(domain, str), 'Invalid domain %s' % domain
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
    
def dngettext(domain, msg, msgp, count):
    '''
    Like @see: ngettext, but look the message up in the specified domain.
    
    @param domain: string
        The domain of the key message.
    @param msg: string
        The key message.
    @param msgp: string
        The plural key message.
    @return: string
        The translated message.
    '''
    assert isinstance(domain, str), 'Invalid domain %s' % domain
    return ngettext(msg, msgp, count)

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

def dpgettext(domain, ctxt, msg):
    '''
    Like @see: dgettext, but use the provided context for the message.
    
    @param domain: string
        The domain of the key message.
    @param ctxt: string
        The context of the key message.
    @param msg: string
        The key message.
    @return: string
        The translated message.
    '''
    assert isinstance(ctxt, str), 'Invalid context %s' % ctxt
    return dgettext(domain, msg)

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

def dnpgettext(domain, ctxt, msg, msgp, count):
    '''
    Like @see: dngettext, but use the provided context for the message.
    
    @param domain: string
        The domain of the key message.
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
    return dngettext(domain, msg, msgp, count)

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
