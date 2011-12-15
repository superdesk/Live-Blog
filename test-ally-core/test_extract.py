'''
Created on Aug 1, 2011
'''
from babel import localedata
from babel.messages.catalog import Catalog
from babel.messages.extract import extract_from_dir
from babel.messages.pofile import write_po
import os
from babel.messages.mofile import write_mo
from babel.numbers import format_decimal

if __name__ == '__main__':
    # We need to adjust the dir name for locales since they need to be outside the .egg file
    localedata._dirname = localedata._dirname.replace('.egg', '')
    print(format_decimal('asa', locale='en_US'))
    catalog = Catalog(locale='en', project='Newscoop', version='3.6',
                      msgid_bugs_address='gabriel.nistor@sourcefabric.org',
                      copyright_holder='2011 Sourcefabric o.p.s.',
                      charset='utf-8')

    extracted = extract_from_dir('e:/Newscoop/AllyPyWork/Newscoop/source')
    for filename, lineno, message, comments in extracted:
        filepath = os.path.normpath(filename)
        catalog.add(message, None, [(filepath, lineno)],
                    auto_comments=comments)
    catalog.add(int.__name__, None, [('NA', 0)])
    catalog.add(float.__name__, None, [('NA', 0)])
    catalog.add(str.__name__, None, [('NA', 0)])
    with open('translation.po', 'wb') as outfile: 
        write_po(outfile, catalog)
    with open('translation.mo', 'wb') as outfile: 
        write_mo(outfile, catalog) 
