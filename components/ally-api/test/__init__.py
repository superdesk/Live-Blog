'''
Created on Jun 1, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Contains the unit tests.
'''

# This is required in order to allow the extension of this package.
import __main__
try: extend = getattr(__main__, 'deployExtendPackage')
except AttributeError: import deploy; extend = __main__.deployExtendPackage = deploy.deployExtendPackage

extend()
