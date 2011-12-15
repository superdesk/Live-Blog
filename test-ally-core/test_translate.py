'''
Created on Aug 4, 2011

@author: chupy
'''

import gettext
import os
from babel.numbers import format_currency
from babel import localedata
from babel.core import Locale
import codecs


if __name__ == '__main__':
    # We need to adjust the dir name for locales since they need to be outside the .egg file
    localedata._dirname = localedata._dirname.replace('.egg', '')
    print(format_currency(1099.98, 'EUR', locale='ro'))
 
    locale = Locale.parse('en')
    print('-----------------', len(locale.languages))
   
    locale = Locale.parse('ro_RO')
    print('-----------------', len(locale.languages))
    
    ids = localedata.locale_identifiers()
    max = 0
    for id in ids:
        if max < len(id):
            max = len(id)
            print(id, '::', max)
        
    codecs.register
    ids = localedata.locale_identifiers()
    for id in ids:
        l = Locale.parse(id)
        assert isinstance(l, Locale)
        name = locale.languages.get(l.language)
        if name is None:
            print('-----------------', l.language)
        else:
            if l.territory or l.script or l.variant:
                details = []
                if l.script:
                    details.append(locale.scripts.get(l.script))
                if l.territory:
                    details.append(locale.territories.get(l.territory))
                if l.variant:
                    details.append(locale.variants.get(l.variant))
                details = [_f for _f in details if _f]
                if details:
                    name += ' (%s)' % ', '.join(details)
            print(name.encode('utf-8'))
#    
    lang = gettext.translation('ally', os.path.dirname(__file__), languages=['ro'])
    _ = lang.gettext
    print(_('Successfully updated'))
