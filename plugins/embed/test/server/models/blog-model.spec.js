/*global describe, it, before, beforeEach, after, afterEach, expect, requirejs, sinon */
/*jshint unused: false, -W030, -W024 */
'use strict';

describe('Model blog', function() {
    var request = require('request');
    var Blog, Posts;

    beforeEach(function(done) {
        requirejs(['models/blog', 'collections/posts'], function(BlogClass, PostsClass) {
            Blog = BlogClass;
            Posts = PostsClass;
            done();
        });
    });
    describe('parse', function() {
        it('parse received data', function() {
            var blog = new Blog(),
                blogData,
                embedConfigData = {
                    Id: 1,
                    EmbedConfig: '{"UserComments": true, "FrontendServer": "//localhost:8080"}'
                },
                data = {
                    Title: 'test title'
                };
            blogData = blog.parse(data);
            expect(blogData).to.not.have.property('Id');

            expect(blogData).to.have.property('Title').and.equal('test title');

            expect(blogData).to.have.property('EmbedConfig').to.be.an('object').and.to.be.empty;

            blogData = blog.parse(embedConfigData);

            expect(blogData).to.have.property('Id').and.to.equal(1);
            expect(blogData).to.have.deep.property('EmbedConfig.UserComments')
                                    .and.to.equal.true;
            expect(blogData).to.have.deep.property('EmbedConfig.FrontendServer')
                                    .and.to.equal('//localhost:8080');
        });
    });
    describe('urlRoot', function() {
        it('get urlRoot for blog model', function() {
            var blog = new Blog();
            GLOBAL.liveblog = {
                servers: {
                    rest: '//localhost:8080'
                }
            };
            expect(blog.urlRoot()).to.equal('//localhost:8080/resources/LiveDesk/Blog/');
        });
    });

    describe('initialize', function() {
        it('initialize for blog model with publishedPosts data and poller', function() {
            var blog = new Blog({Id: 2});
            expect(blog).to.not.have.property('timeoutId');
            expect(blog.get('publishedPosts')).to.be.an.instanceof(Posts)
                                                .and.to.have.property('blogId').to.equal(2);
        });
    });

    describe('properties', function() {
        it('blog model should have defined properties', function() {
            var blog = new Blog();
            expect(blog).to.have.property('pollInterval');
            expect(blog).to.have.deep.property('syncParams.headers.X-Filter').and
                                        .to.contain('Language.Code')
                                        .to.contain('EmbedConfig')
                                        .to.contain('Description')
                                        .to.contain('Title');
            expect(blog).to.have.deep.property('syncParams.updates').and
                                        .to.be.an('object').and
                                            .to.be.empty;
        });
    });

    describe('fetch', function() {
        // Use Sinon to replace jQuery's ajax method
        // with a spy.
        beforeEach(function() {
            sinon.stub(request, 'get').yieldsTo(null, null,
                {
                    statusCode: 200
                }, {
                    Id: 1,
                    Title: 'test title',
                    Language: {
                        Code: 'de'
                    },
                    EmbedConfig: '{"UserComments": true, "FrontendServer": "//localhost:8080"}'
                });
        });

        // Restor jQuery's ajax method to its
        // original state
        afterEach(function() {
            request.get.restore();
        });
        it('blog model should make an ajax call to liveblog.server.rest', function(done) {
            var blog = new Blog({Id: 1});
            GLOBAL.liveblog = {
                servers: {
                    rest: '//localhost:8080'
                }
            };
            blog.fetch();
            expect(request.get.calledOnce).to.be.true;
            expect(request.get.getCall(0).args[0].url).to.equal('//localhost:8080/resources/LiveDesk/Blog/1');
            expect(request.get.getCall(0).args[0].headers).to.have.property('X-Format-DateTime').and.to.equal('yyyy-MM-ddTHH:mm:ss\'Z\'');
            expect(blog.get('Id')).equal(1);
            expect(blog.get('Title')).equal('test title');
            expect(blog.get('EmbedConfig')).to.have.property('UserComments')
                                    .and.to.equal.true;
            expect(blog.get('EmbedConfig')).to.have.property('FrontendServer')
                                    .and.to.equal('//localhost:8080');
            expect(blog.get('Language')).to.have.property('Code')
                                    .and.to.equal('de');
            done(); // let Mocha know we're done async testing
        });
    });
});
