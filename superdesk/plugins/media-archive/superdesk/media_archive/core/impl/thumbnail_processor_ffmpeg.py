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
from ally.container.support import setup
from ally.support.util_io import synchronizeURIToDir
from ally.support.util_sys import pythonPath
from genericpath import exists
from os.path import join, abspath, dirname
from os import makedirs
from subprocess import Popen
from superdesk.media_archive.core.spec import IThumbnailProcessor
import logging
import os

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
@setup(IThumbnailProcessor)
class ThumbnailProcessor(IThumbnailProcessor):
    '''
    Implementation for @see: IThumbnailProcessor
    '''

    command_transform = '%(ffmpeg)s -i %(source)s %(destination)s'; wire.config('command_transform', doc='''
    The command used to transform the thumbnails''')
    command_resize = '%(ffmpeg)s -i %(source)s -s %(width)ix%(height)i %(destination)s'
    wire.config('command_resize', doc='''The command used to resize the thumbnails''')
    ffmpeg_dir_path = join('workspace', 'tools', 'ffmpeg'); wire.config('ffmpeg_dir_path', doc='''
    The path where the ffmpeg is placed in order to be used, if empty will not place the contained ffmpeg''')
    ffmpeg_path = join(ffmpeg_dir_path, 'bin', 'ffmpeg'); wire.config('ffmpeg_path', doc='''
    The path where the ffmpeg is found''')

    def __init__(self):
        assert isinstance(self.command_transform, str), 'Invalid command transform %s' % self.command_transform
        assert isinstance(self.command_resize, str), 'Invalid command resize %s' % self.command_resize
        assert isinstance(self.ffmpeg_dir_path, str), 'Invalid ffmpeg directory %s' % self.ffmpeg_dir_path
        assert isinstance(self.ffmpeg_path, str), 'Invalid ffmpeg path %s' % self.ffmpeg_path

        if self.ffmpeg_dir_path: synchronizeURIToDir(join(pythonPath(), 'resources', 'ffmpeg'), self.ffmpeg_dir_path)

    def processThumbnail(self, source, destination, width=None, height=None):
        '''
        @see: IThumbnailProcessor.processThumbnail
        '''
        assert isinstance(source, str), 'Invalid source path %s' % source
        assert isinstance(destination, str), 'Invalid destination path %s' % destination

        params = dict(ffmpeg=abspath(self.ffmpeg_path), source=source, destination=destination)
        if width and height:
            assert isinstance(width, int), 'Invalid width %s' % width
            assert isinstance(height, int), 'Invalid height %s' % height

            params.update(width=width, height=height)
            command = self.command_resize
        else: command = self.command_transform
        args = command.split()
        args = [arg % params for arg in args]

        destDir = dirname(destination)
        if not exists(destDir): makedirs(destDir)
        try:
            p = Popen(args)
            error = p.wait() != 0
        except Exception as e:
            log.exception('Problems while executing command:\n%s \n%s' % (command, e))
            error = True

        if error:
            if exists(destination): os.remove(destination)
            raise IOError('Cannot process thumbnail from \'%s\' to \'%s\'' % (source, destination))

