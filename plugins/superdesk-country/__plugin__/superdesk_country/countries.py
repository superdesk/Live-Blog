'''
Created on Mar 9, 2012

@package: Superdesk countries
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Provides the ISO XML source of the setup file. The XML is downloaded from:
http://www.iso.org/iso/country_codes/iso_3166_code_lists.htm
'''

from ally.container import ioc
from ally.support.util_io import openURI
from ally.xml.digester import Digester, RuleRoot
from ally.xml.digester_rules import RuleCreate, RuleSet, RuleSetContent
from os import path
from superdesk.country.impl.country import Countries
from xml.sax.xmlreader import InputSource

# --------------------------------------------------------------------

@ioc.entity
def countriesSource() -> InputSource:
    '''
    Provides the countries input source for the XML.
    '''
    source = InputSource()
    source.setByteStream(openURI(path.join(path.dirname(__file__), 'iso_3166-1_list_en.xml')))
    return source

@ioc.entity
def countries() -> Countries:
    '''
    Provides the countries based on the ISO file.
    '''
    # Parsing the ISO XML to extract the codes and names for countries
    root = RuleRoot()
    entry = root.addRule(RuleCreate(lambda:[None, None]), 'ISO_3166-1_List_en', 'ISO_3166-1_Entry')
    entry.addRule(RuleSet(lambda countries, entry: countries.__setitem__(*entry), 0, -1))
    entry.addRule(RuleSetContent(lambda entry, code: entry.__setitem__(0, code)), 'ISO_3166-1_Alpha-2_Code_element')
    entry.addRule(RuleSetContent(lambda entry, name: entry.__setitem__(1, name)), 'ISO_3166-1_Country_name')

    digester = Digester(root)
    digester.stack.append(Countries())
    return digester.parseInputSource(countriesSource())
