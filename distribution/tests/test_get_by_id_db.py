'''
Created on Nov 24, 2011

@package: tests
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Test a get by id that it is known to hit the database.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(False)
    import warnings
    warnings.filterwarnings('ignore', '.*already imported.*ally*')
    # To remove the warnings of pkg utils from setup tools
# --------------------------------------------------------------------

import profile
from test_support.application_no_server import start
from test_support.chain_support import compileProcessings, processGet
import timeit
from threading import Thread
import sys
from ally.design.processor import Processing
import pickle
from multiprocessing import Process, Pool, Pipe, Lock, Condition, Array
from multiprocessing import forking
from ally.container import ioc, support, aop
from ally.container._impl.ioc_setup import Assembly
from ctypes import c_byte
import json

# --------------------------------------------------------------------

def processGetUserById(number, pathProcessing):
    getUser = lambda : processGet(pathProcessing, {'Host': 'localhost'}, '/resources/Superdesk/User/1')
    runTime = timeit.timeit(getUser, number=number)
    print('Made %s get User requests in %s seconds, meaning %s requests/second' % (number, runTime, number / runTime))

def processGetRequestById(number, pathProcessing):
    getUser = lambda : processGet(pathProcessing, {'Host': 'localhost'}, '/resources/Devel/Request/1')
    runTime = timeit.timeit(getUser, number=number)
    print('Made %s get Request requests in %s seconds, meaning %s requests/second' % (number, runTime, number / runTime))

def processGetLanguageByCode(number, pathProcessing):
    getUser = lambda : processGet(pathProcessing, {'Host': 'localhost'}, '/resources/Superdesk/Language/en')
    runTime = timeit.timeit(getUser, number=number)
    print('Made %s get Language requests in %s seconds, meaning %s requests/second' % (number, runTime, number / runTime))

# --------------------------------------------------------------------

def processsInThread(k, fn, *agrs):
    t = Thread(target=fn, name='Thread %s' % k, args=agrs)
    print('CREATED:', t, id(t), t.ident)
    t.start()
    t.join()

def processsInThreadSplit(k, fn, number, pathProcessing, count=20):
    threads = []
    for k in range(0, count):
        t = Thread(target=fn, name='Thread %s' % k, args=(int(number / count), pathProcessing))
        t.start()
        threads.append(t)
    
    for t in threads: t.join()
    
# --------------------------------------------------------------------

def processRegisteredGetLanguageByCode(number):
    global PATH_PROCESSING
    getUser = lambda : processGet(PATH_PROCESSING, {'Host': 'localhost'}, '/resources/Superdesk/Language/en')
    runTime = timeit.timeit(getUser, number=number)
    print('Made %s get Language requests in %s seconds, meaning %s requests/second' % (number, runTime, number / runTime))

def processRegisteredGetUserById(number):
    getUser = lambda : processGet(PATH_PROCESSING, {'Host': 'localhost'}, '/resources/Superdesk/User/1')
    runTime = timeit.timeit(getUser, number=number)
    print('Made %s get User requests in %s seconds, meaning %s requests/second' % (number, runTime, number / runTime))

def testResponse(pathProcessing):
    processing = pathProcessing[0][1]
    assert isinstance(processing, Processing)
    ResponseContent = processing.contexts['responseCnt']
    rspCnt = ResponseContent()
    
    print(pickle.dumps(('MUMU', 'RURU')))
    print(pickle.dumps(rspCnt))

# --------------------------------------------------------------------

# EXCLUDED = []

EXCLUDED = ['ally-authentication-core', 'ally-authentication-http',
            'livedesk', 'ffmpeg-binary', 'media-archive', 'media-archive', 'media-archive-audio', 'media-archive-image',
            'media-archive-video', 'superdesk-address', 'superdesk-authentication', 'superdesk-collaborator',
            'superdesk-country', 'superdesk-post', 'superdesk-source']

# EXCLUDED = ['livedesk', 'ffmpeg-binary', 'media-archive', 'media-archive', 'media-archive-audio', 'media-archive-image',
#            'media-archive-video', 'superdesk-address', 'superdesk-authentication', 'superdesk-collaborator',
#            'superdesk-country', 'superdesk-language', 'superdesk-post', 'superdesk-source']
    
# --------------------------------------------------------------------

def createProcessings():
    global PATH_PROCESSING
    PATH_PROCESSING = compileProcessings(start())
    print('=' * 50)
    
# --------------------------------------------------------------------

if __name__ == '__main__':
    paths = []
    for path in sys.path:
        for exclude in EXCLUDED:
            if path.endswith(exclude): break
        else: paths.append(path)
    sys.path = paths

    pathProcessing = compileProcessings(start())
    print('=' * 50)
    
#    testResponse(pathProcessing)
    
#    global PATH_PROCESSING
#    PATH_PROCESSING = pathProcessing
#    profile.run('processGetLanguageByCode(100, PATH_PROCESSING)', 'profile.data')
    
    number, counts = 3000, 4

# ----------------------------------------------------------------------------------------------------
    
#    processes = []
#    for k in range(0, counts):
# #        if k == 0:
# #            process = Process(target=processsInThreadSplit, args=(k, processGetUserById, int(number / counts), pathProcessing))
# #        else: process = Process(target=processGetUserById, args=(int(number / counts), pathProcessing))
#        process = Process(target=processsInThreadSplit, args=(k, processGetUserById, int(number / counts), pathProcessing))
#        process.start()
#        processes.append(process)
#    
#    for process in processes: process.join()

 
#    processes = []
#    for k in range(0, counts):
#        process = Process(target=processsInThread,
#                          args=(k, processGetLanguageByCode, int(number / counts), pathProcessing))
#        process.start()
#        processes.append(process)
#    
#    for process in processes: process.join()

# ----------------------------------------------------------------------------------------------------
#    pool = Pool(counts, registerPathProcessing, (pathProcessing,))
#    for k in range(0, counts):
#        pool.apply_async(processRegisteredGetUserById, (int(number / counts),))
#    pool.close()
#    pool.join()

# ----------------------------------------------------------------------------------------------------
#    processGetUserById(number, pathProcessing)
    
#    Thread(target=processGetRequestById, args=(number, pathProcessing)).start()
#    Thread(target=processGetRequestById, args=(int(number / 2), pathProcessing)).start()
#    Thread(target=processGetRequestById, args=(int(number / 2), pathProcessing)).start()
    
#    processGetRequestById(number, pathProcessing)
    
#    processGetLanguageByCode(number, pathProcessing)
#    Thread(target=processGetLanguageByCode, args=(int(number / 2), pathProcessing)).start()
#    Thread(target=processGetLanguageByCode, args=(int(number / 2), pathProcessing)).start()

# ----------------------------------------------------------------------------------------------------
#    pool = Pool(counts, registerPathProcessing, (pathProcessing,))
#    for k in range(0, counts):
#        pool.apply_async(processRegisteredGetUserById, (int(number / counts),))
#    pool.close()
#    pool.join()

# ====================================================================================================
# ====================================================================================================
# ====================================================================================================

#    def testDispatchGroups():
#        def processGetLanguageByCode(number, pathProcessing):
#            getUser = lambda : processGet(pathProcessing, {'Host': 'localhost'}, '/resources/Superdesk/Language/en')
#            for _k in range(0, number): getUser()
#    
#        processes = []
#        for _k in range(0, counts):
#            process = Process(target=processGetLanguageByCode, args=(int(number / counts), pathProcessing))
#            process.start()
#            processes.append(process)
#        
#        for process in processes: process.join()
#        
#    runTime = timeit.timeit(testDispatchGroups, number=1)
#    print('Made %s requests in %s seconds, meaning %s requests/second' % (number, runTime, number / runTime))

# ----------------------------------------------------------------------------------------------------

#    def register(pathProcessing):
#        global PATH_PROCESSING
#        PATH_PROCESSING = pathProcessing 
#
#    def get(headers, url):
#        global PATH_PROCESSING
#        return processGet(PATH_PROCESSING, headers, url)
#
#    def testDispatch():
#        pool = Pool(counts, register, (pathProcessing,))
#        for _k in range(0, number):
#            # pool.apply_async(get, ({'Host': 'localhost'}, '/resources/Superdesk/User/1'))
#            pool.apply_async(get, ({'Host': 'localhost'}, '/resources/Superdesk/Language/en'))
#        pool.close()
#        pool.join()
#    
#    runTime = timeit.timeit(testDispatch, number=1)
#    print('Made %s requests in %s seconds, meaning %s requests/second' % (number, runTime, number / runTime))

# ----------------------------------------------------------------------------------------------------

#    def deploy(pathProcessing, pipe):
#        
#        while True:
#            data = pipe.recv()
#            if data is None: break
#            processGet(pathProcessing, data[0], data[1])
#
#    def testDispatch():
#        processes, pipes = [], []
#        for k in range(0, counts):
#            parent, child = Pipe()
#            process = Process(name='Process %s' % k, target=deploy, args=(pathProcessing, child))
#            processes.append(process)
#            pipes.append(parent)
#            process.start()
#            
#        for _k in range(0, int(number / counts)):
#            for k in range(0, counts):
#                pipes[k].send(({'Host': 'localhost'}, '/resources/Superdesk/User/1'))
#                # pipes[k].send(({'Host': 'localhost'}, '/resources/Superdesk/Language/en'))
#                
#        for k in range(0, counts): pipes[k].send(None)
#        
#        for process in processes: process.join()
#    
#    runTime = timeit.timeit(testDispatch, number=1)
#    print('Made %s requests in %s seconds, meaning %s requests/second' % (number, runTime, number / runTime))
