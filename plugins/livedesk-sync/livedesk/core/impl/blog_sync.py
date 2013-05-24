'''
Created on April 26, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API implementation of liveblog sync.
'''

from sched import scheduler
from threading import Thread
from datetime import time
from livedesk.api.blog_sync import IBlogSyncService

# --------------------------------------------------------------------

class BlogSyncService(IBlogSyncService):
    '''
    Blog sync implementation.
    '''

    syncInterval = float
    # The number of seconds to perform sync for blogs.

    def startSyncThread(self, name):
        '''
        Starts the sync thread.

        @param name: string
            The name for the thread.
        '''
        schedule = scheduler(time.time, time.sleep)
        def syncBlogs():
            self.syncBlogs()
            schedule.enter(self.syncInterval, 1, syncBlogs, ())
        schedule.enter(self.syncInterval, 1, syncBlogs, ())
        scheduleRunner = Thread(name=name, target=schedule.run)
        scheduleRunner.daemon = True
        scheduleRunner.start()

    def syncBlogs(self):
        '''
        '''
