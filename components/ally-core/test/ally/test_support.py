'''
Created on Jan 28, 2012

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides test support classes.
'''

from ally.core.spec.server import EncoderPath

# --------------------------------------------------------------------

class EncoderGetObj:
    
    def __init__(self):
        self.obj = None
    
    def __call__(self, obj, *args):
        self.obj = obj
        return ['Nothing']

# --------------------------------------------------------------------

class EncoderPathTest(EncoderPath):
    
    def __init__(self, converterPath):
        self.converterPath = converterPath
    
    def encode(self, path, parameters=None):
        return '/'.join(path.toPaths(self.converterPath))
