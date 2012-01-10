'''
Created on Jan 9, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the aop module.
'''

# Required in order to register the package extender whenever the unit test is run.
import package_extender
package_extender.registerPackageExtender()

import unittest
from ally.container import aop

# --------------------------------------------------------------------

modules = ['test.ally.container.aop_sample.pckg1.modul1_1', 'test.ally.container.aop_sample.pckg1.modul1_2',
           'test.ally.container.aop_sample.pck2.modul2_1', 'test.ally.container.aop_sample.pck2.modul2_2']

# --------------------------------------------------------------------

class TestAOP(unittest.TestCase):
        
    def testModules(self):
        aopm = aop.modulesIn('test.ally.container.aop_sample.*.*')
        self.assertTrue(modules == aopm.asList())
        aopm.load()
        
        aopm = aop.modulesIn('test.ally.container.aop_sample.*.*')
        self.assertTrue(modules == aopm.asList())
        
# --------------------------------------------------------------------
  
if __name__ == '__main__':
    #unittest.main()
    aopm = aop.modulesIn('test.ally.container.aop_sample.*.*')
    print(aopm.asList())
    aopm.load()
    
    aopm = aop.modulesIn('test.ally.container.aop_sample.*.*')
    print(aopm.asList())