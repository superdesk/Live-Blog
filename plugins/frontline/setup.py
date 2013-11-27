
'''
Created on Oct 1, 2013
 
@package: distribution_manager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
Auto-generated setup configuration for components/plugins needed for pypi.
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(packages=find_packages('.'),
      platforms=['all'],
      zip_safe=True,
      license='GPL v3',
      url='http://www.sourcefabric.org/en/superdesk/', # project home page
           description='Superdesk frontline API plugin',
     author='Martin Saturka',
     install_requires=['ally-api >= 1.0', 'support-sqlalchemy >= 1.0', 'ally-plugin >= 1.0', 'superdesk >= 1.0'],
     author_email='martin.saturka@sourcefabric.org',
     version='1.0',
     keywords=['Ally', 'REST', 'Superdesk', 'plugin', 'Frontline'],
     long_description='Superdesk frontline API plugin',
     name='frontline',

     )