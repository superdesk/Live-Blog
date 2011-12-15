'''
Created on Nov 25, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the loader module.
'''

import unittest
from ally.ioc.context import ContextIoC

# --------------------------------------------------------------------

class TestLoader(unittest.TestCase):

    def testSucces(self):
        ctx = ContextIoC()
        ctx.addSetup('sample1', \
'''
from inspect import isfunction

person = lambda _config = {
                                    'name': 'Gabriel'
                                }: {_config['name']}

def job(ctx, _config:'A config'):
    b = {'person':ctx.person}; yield b
    b['job'] = 'Developer'
    print(b)
''')
        self.assertTrue('sample1.person.config' in ctx._Context__setupConfigurations)
        self.assertTrue('sample1.person' in ctx._Context__setupFunctions)
        self.assertTrue('sample1.job' in ctx._Context__setupFunctions)
        self.assertFalse('sample1.isfunction' in ctx._Context__setupFunctions)
        
        ctx.assemble()
        
        #ctx.addModule('ally.ioc_test.setup_sample.sample_1')

    # ----------------------------------------------------------------
    
    def testFailed(self):
        pass
        
# --------------------------------------------------------------------

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
