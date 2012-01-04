'''
Created on Jun 1, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Contains all the modules that are used for describing and configuring API services and models. A general description
will be that the modules are used for describing types for models, call inputs and outputs and the *configure* module
provides the means for generating this description objects by using python decorators and descriptors.
'''

# This is required in order to allow the extension of this package.
try: from __main__ import deployExtendPackage
except ImportError: pass
else: deployExtendPackage()