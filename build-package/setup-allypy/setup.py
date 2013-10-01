'''
Created on Sep 25, 2013

@package: Liveblog
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name="ally-py",
    version="0.9.0",
    packages=find_packages(),
    install_requires=['Babel>=1.0', 'pytz', 'httplib2>=0.7', 'MySql-connector-python>=0.3', 'PyYAML>=3.0', 'SQLAlchemy>=0.7'],
    platforms=['all'],
    zip_safe=True,
    py_modules=['package_extender', 'application'],
    package_data={'': ['*.txt', '*.conf', '*.zip', '*.html', '*.dust', '*.css', '*.less', '*.js',
                       '*.eot', '*.svg', '*.ttf', '*.woff', '*.otf', '*.png', '*.jpg', '*.gif']},

    # metadata for upload to PyPI
    author="Sourcefabric",
    author_email="contact@sourcefabric.org",
    description="Ally-Py",
    long_description='REST development framework',
    license="GPL v3",
    keywords="Liveblog",
    url="http://www.sourcefabric.org/en/superdesk/",
    classifiers=[
                 'Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.2',
                 'Topic :: Software Development :: Libraries :: Application Frameworks'
                 ]
)
