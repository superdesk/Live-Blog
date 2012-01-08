'''
Created on Jun 1, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Contains the unit tests.
'''

# Required in order to register the package extender whenever the unit test is run.
try:
    import deploy
    deploy.registerPackageExtender()
except ImportError: pass
