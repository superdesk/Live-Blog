'''
Created on April 4, 2014

@package: REST API tests for embed 
@copyright: 2014 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

REST API tests for embed
'''

from api_test_tool.api_testclass import ApiTestCase
import datetime
import os

class PostsTestCase(ApiTestCase):
    
    def getIdFromHref(self):
        path = self._parse_json_response()['href']
        return os.path.basename(path) 
    
    def setUp(self):
        start = datetime.datetime.now()
        
        self.PUT('/Tool/TestFixture/default', 
                  {'Name' : 'default',
                   'ApplyOnDatabase' : True,
                   'ApplyOnFiles' : True},
                  with_auth=False
                  )
        self.expect_status(200)
        
        print('populate: ', datetime.datetime.now() - start)
        
        #get all published posts
        self.GET('/LiveDesk/Blog/1/Post/Published')
        self.expect_status(200)
        self.expect_json({'lastCId': '7', 'total': '6'}, partly=True)
            
        #check that on get all publish changed since last added post -> empty list  
        self.GET('/LiveDesk/Blog/1/Post/Published?cId.since=7')
        self.expect_status(200)
        self.expect_json({'PostList': [], 'lastCId': '7'}, partly=True)
            
        #add a post  
        self.POST('/my/LiveDesk/Blog/1/Post', 
                  {'Meta': '{}', 'Content': 'test', 'Type' : 'normal', 'Creator' : '1'})
        self.expect_status(201)
        self.lastId = self.getIdFromHref()
          
        #check that no post is not published   
        self.GET('/LiveDesk/Blog/1/Post/Published?cId.since=7')
        self.expect_status(200)
        self.expect_json({'PostList': [], 'lastCId': '8'}, partly=True)
          
        #publish post   
        self.POST('/my/LiveDesk/Blog/1/Post/%(id)s/Publish' % {'id': self.lastId})
        self.expect_status(201)
        
        
    def test_add_posts(self):
        #check that get publish changed since post added is returning one item    
        self.GET('/LiveDesk/Blog/1/Post/Published?cId.since=8')
        self.expect_status(200)
        self.expect_json({'total': '1', 'lastCId': '9'}, partly=True)
           
        #check if the post is published
        self.GET('/my/LiveDesk/Blog/1/Post/%(id)s' % {'id': self.lastId})
        self.expect_status(200)
        self.expect_json({'Id': self.lastId, 'IsPublished': 'True'}, partly=True)
       
       
    def test_edit_posts(self):             
        #edit post    
        self.PUT('/my/LiveDesk/Blog/1/Post/%(id)s' % {'id': self.lastId}, 
                  {'Content': 'test changed'})
        self.expect_status(200)
    
        #check that the publish changes return one row
        self.GET('/LiveDesk/Blog/1/Post/Published?cId.since=9')
        self.expect_status(200)
        self.expect_json({'total': '1', 'lastCId': '10'}, partly=True)
   
        #check if the post is changed
        self.GET('/my/LiveDesk/Blog/1/Post/%(id)s' % {'id': self.lastId})
        self.expect_status(200)
        self.expect_json({'Id': self.lastId, 'IsPublished': 'True', 'Content': 'test changed'}, partly=True)
 
 
    def test_unpublish_posts(self):    
        #unpublish post     
        self.POST('/my/LiveDesk/Blog/1/Post/%(id)s/Unpublish' % {'id': self.lastId}, 
                  {'Content': 'test changed'})
        self.expect_status(201)
           
        #check that the list of publish changes contains one item
        self.GET('/LiveDesk/Blog/1/Post/Published?cId.since=9', 
                 headers={'X-Filter': 'Id,IsPublished'})
        self.expect_status(200)
        self.expect_json({'total': '1', 'lastCId': '10'}, partly=True)
   
        #check if the post is unpublished
        self.GET('/my/LiveDesk/Blog/1/Post/%(id)s' % {'id': self.lastId})
        self.expect_status(200)
        self.expect_json({'Id': self.lastId, 'IsPublished': 'False'}, partly=True)
 
 
    def test_delete_posts(self):  
        #delete post     
        self.DELETE('/my/Data/Post/%(id)s' % {'id': self.lastId})
        self.expect_status(204)
          
        #check that the list of publish changes contains one item
        self.GET('/LiveDesk/Blog/1/Post/Published?cId.since=9', 
                 headers={'X-Filter': 'Id,IsPublished'})
        self.expect_status(200)
        self.expect_json({'total': '1', 'lastCId': '10'}, partly=True)
  
        #check if the post is deleted
        self.GET('/my/LiveDesk/Blog/1/Post/%(id)s' % {'id': self.lastId})
        self.expect_status(200)
        #self.inspect_json()
        
        
    def test_pagination_for_posts(self):  
        for i in range(1, 20):
            self.POST('/my/LiveDesk/Blog/1/Post', 
                      {'Meta': '{}', 'Content': 'test' + str(i), 'Type' : 'normal', 'Creator' : '1'})
            self.expect_status(201)
            lastId = self.getIdFromHref()
             
            #publish post   
            self.POST('/my/LiveDesk/Blog/1/Post/%(id)s/Publish' % {'id': lastId})
            self.expect_status(201)
         
        #first page  
        self.GET('/LiveDesk/Blog/1/Post/Published?limit=15')
        self.expect_status(200)
        self.expect_json_length(15, path='PostList')
         
        #second page
        self.GET('/LiveDesk/Blog/1/Post/Published?offset=15&limit=15')
        self.expect_status(200)
        self.expect_json_length(11, path='PostList')
        
    def test_blog_settings(self):
        #update EmbedConfig
        self.PUT('/my/LiveDesk/Blog/1',
            {'EmbedConfig' : '{"theme":"tageswoche-multi",' +
                              '"FrontendServer":"//localhost:8080",' +
                              '"MediaImage":"//localhost:8080/content/media_archive/audio/000/2.23.jpeg",' +
                              '"VerificationToggle":"on",' +
                              '"MediaToggle":"true",' +
                              '"MediaUrl":"//www.sourcefabric.org",' +
                              '"UserComments":"true"}'
            })
        self.expect_status(200)

            
        #get current blog setting
        self.GET('/LiveDesk/Blog/1')
        self.expect_status(200)
        self.expect_json('{"theme":"tageswoche-multi",' +
                              '"FrontendServer":"//localhost:8080",' +
                              '"MediaImage":"//localhost:8080/content/media_archive/audio/000/2.23.jpeg",' +
                              '"VerificationToggle":"on",' +
                              '"MediaToggle":"true",' +
                              '"MediaUrl":"//www.sourcefabric.org",' +
                              '"UserComments":"true"}'
                          , partly=False, path='EmbedConfig')
     
    