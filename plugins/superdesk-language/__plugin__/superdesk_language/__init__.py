'''
Created on Jul 15, 2011

@package: Superdesk language
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Balaceanu

Contains the superdesk language setup files.
'''

# --------------------------------------------------------------------

NAME = 'Superdesk languages'
GROUP = 'Superdesk'
VERSION = '1.0'
DESCRIPTION = 'Provides the the Superdesk languages'

from babel import localedata, core
# Babel FIX: We need to adjust the dir name for locales since they need to be outside the .egg file
localedata._dirname = localedata._dirname.replace('.egg', '')
core._filename = core._filename.replace('.egg', '')
