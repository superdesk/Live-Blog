'''
Created on Sep 1, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the Babel configuration.
'''

# --------------------------------------------------------------------

from babel import localedata, core
# Babel FIX: We need to adjust the dir name for locales since they need to be outside the .egg file
localedata._dirname = localedata._dirname.replace('.egg', '')
core._filename = core._filename.replace('.egg', '')

# --------------------------------------------------------------------
