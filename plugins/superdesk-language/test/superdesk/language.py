'''
Created on Feb 21, 2012

@package: superdesk
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the language module.
'''

import unittest
from superdesk.language.impl.language import LanguageServiceBabelAlchemy
from superdesk.language.api.language import QLanguage
from ally.container import ioc
import pstats
from profile import Profile

# --------------------------------------------------------------------

class TestLanguage(unittest.TestCase):
        
    def testPerformance(self):
        from babel import localedata, core
        # Babel FIX: We need to adjust the dir name for locales since they need to be outside the .egg file
        localedata._dirname = localedata._dirname.replace('.egg', '')
        core._filename = core._filename.replace('.egg', '')
    
        languageService = LanguageServiceBabelAlchemy()
        ioc.initialize(languageService)
        
        profile = Profile()
        qlang = QLanguage(name='rom%')
        try:
            profile = profile.runctx("languageService.getAllAvailable(0, 10, qlang, None)", globals(), locals())
        except SystemExit: pass
        pstats.Stats(profile).sort_stats('time', 'cum').print_stats()
        
# --------------------------------------------------------------------
  
if __name__ == '__main__':
    unittest.main()
