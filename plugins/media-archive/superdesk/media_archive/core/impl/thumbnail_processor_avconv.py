'''
Created on Sep 11, 2012

@package: media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Thumbnail processor class definition.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.support.util_io import synchronizeURIToDir
from ally.support.util_sys import pythonPath
from genericpath import exists
from os import makedirs
from os.path import join, abspath, dirname
from subprocess import Popen
from superdesk.media_archive.core.spec import IThumbnailProcessor
import logging
import os

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class ThumbnailProcessorAVConv(IThumbnailProcessor):
    '''
    Implementation for @see: IThumbnailProcessor
    '''

    command_transform = '"%(avconv)s" -i "%(source)s" "%(destination)s"'; wire.config('command_transform', doc='''
    The command used to transform the thumbnails''')
    command_resize = '"%(avconv)s" -i "%(source)s" -s %(width)ix%(height)i "%(destination)s"'
    wire.config('command_resize', doc='''The command used to resize the thumbnails''')
    avconv_dir_path = join('workspace', 'tools', 'avconv'); wire.config('avconv_dir_path', doc='''
    The path where the avconv is placed in order to be used, if empty will not place the contained avconv''')
    avconv_path = join(avconv_dir_path, 'bin', 'avconv'); wire.config('avconv_path', doc='''
    The path where the avconv is found''')

    def __init__(self):
        assert isinstance(self.command_transform, str), 'Invalid command transform %s' % self.command_transform
        assert isinstance(self.command_resize, str), 'Invalid command resize %s' % self.command_resize
        assert isinstance(self.avconv_dir_path, str), 'Invalid avconv directory %s' % self.avconv_dir_path
        assert isinstance(self.avconv_path, str), 'Invalid avconv path %s' % self.avconv_path

        if self.avconv_dir_path: synchronizeURIToDir(join(pythonPath(), 'resources', 'avconv'), self.avconv_dir_path)

    def processThumbnail(self, source, destination, width=None, height=None):
        '''
        @see: IThumbnailProcessor.processThumbnail
        '''
        assert isinstance(source, str), 'Invalid source path %s' % source
        assert isinstance(destination, str), 'Invalid destination path %s' % destination

        params = dict(avconv=abspath(self.avconv_path), source=source, destination=destination)
        if width and height:
            assert isinstance(width, int), 'Invalid width %s' % width
            assert isinstance(height, int), 'Invalid height %s' % height

            params.update(width=width, height=height)
            command = self.command_resize % params

        elif height:
            assert isinstance(height, int), 'Invalid height %s' % height
            width = int((16 / 9) * height)

            params.update(width=width, height=height)
            command = self.command_resize % params

        else: command = self.command_transform % params

        destDir = dirname(destination)
        if not exists(destDir): makedirs(destDir)
        try:
            p = Popen(command)
            error = p.wait() != 0
        except:
            log.exception('Problems while executing command:\n % s', command)
            error = True

        if error:
            if exists(destination): os.remove(destination)
            raise IOError('Cannot process thumbnail from \'%s\' to \'%s\'' % (source, destination))

