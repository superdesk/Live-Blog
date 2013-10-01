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
    name="ally_py",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    platforms=['all'],
    zip_safe=True,
    py_modules=['package_extender', 'application'],
    package_data={'': ['*.txt', '*.conf', '*.zip', '*.html', '*.dust', '*.css', '*.less', '*.js',
                       '*.eot', '*.svg', '*.ttf', '*.woff', '*.otf', '*.png', '*.jpg', '*.gif']},
    include_package_data=True,

    # metadata for upload to PyPI
    author="Sourcefabric",
    author_email="contact@sourcefabric.org",
    description="Ally-Py",
    long_description='REST development framework',
    license="GPL v3",
    keywords="Liveblog",
    url="http://www.sourcefabric.org/en/superdesk/", # project home page
)
