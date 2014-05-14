// TODO: Set a different jshint config for tests and remove the next lines
/*global describe, it, before, beforeEach, after, afterEach, expect, sinon */
/*jshint unused: false, -W030, -W024 */
'use strict';

define(['jquery', 'models/blog', 'collections/posts'], function($, Blog, Posts) {
    describe('Model blog', function() {
        describe('parse', function() {
            var blog = new Blog(),
                dataTitle,
                dataEmbedConfig,
                embedConfigData = {
                    Id: 1,
                    EmbedConfig: '{"UserComments": true, "FrontendServer": "//localhost:8080"}'
                },
                data = {
                    Title: 'test title'
                };
            dataTitle = blog.parse(data);
            dataEmbedConfig = blog.parse(embedConfigData);

            it('shouldn\'t have id field', function() {
                expect(dataTitle).to.not.have.property('Id');
            });

            it('should have title field as "test title"', function() {
                expect(dataTitle).to.have.property('Title').and.equal('test title');
            });

            it('should have EmbedConfig object field empty', function() {
                expect(dataTitle).to.have.property('EmbedConfig').to.be.an('object')
                                                .and.to.be.empty;
            });

            it('shouldn have id integer field', function() {
                expect(dataEmbedConfig).to.have.property('Id')
                                                .and.to.be.a('number')
                                                .and.to.equal(1);
            });
            it('should have EmbedConfig.UserComments boolean field', function() {
                expect(dataEmbedConfig).to.have.deep.property('EmbedConfig.UserComments')
                                                .and.be.a('boolean')
                                                .and.to.equal.true;
            });
            it('should have EmbedConfig.FrontendServer string field equal to "//localhost:8080"', function() {
                expect(dataEmbedConfig).to.have.deep.property('EmbedConfig.FrontendServer')
                                        .and.to.equal('//localhost:8080');
            });
            blog.stopPolling();
        });
        // test the urlRoot method so it will always return the correct url for blog.
        describe('urlRoot', function() {
            var blog = new Blog();
            window.liveblog = {
                servers: {
                    rest: '//localhost:8080'
                }
            };
            it('get urlRoot for blog model', function() {
                expect(blog.urlRoot()).to.equal('//localhost:8080/resources/LiveDesk/Blog/');
            });
            blog.stopPolling();
        });

        describe('initialize', function() {
            var blog = new Blog({Id: 2});

            it('should have timeoutId integer field', function() {
                expect(blog).to.have.property('timeoutId');
            });

            it('should have publishedPosts field instanceof Posts', function() {
                expect(blog.get('publishedPosts')).to.be.an.instanceof(Posts);
            });

            it('should have blogId integer field', function() {
                expect(blog.get('publishedPosts')).to.be.an.instanceof(Posts)
                    .and.to.have.property('blogId').to.equal(2);
            });
            blog.stopPolling();
        });

        describe('properties', function() {
            var blog = new Blog();
            it('should have pollInterval number field', function() {
                expect(blog).to.have.property('pollInterval').to.be.a('number');
            });

            it('should have header X-Filter field', function() {
                expect(blog).to.have.deep.property('syncParams.headers.X-Filter').and
                                            .to.contain('Language.Code')
                                            .to.contain('EmbedConfig')
                                            .to.contain('Description')
                                            .to.contain('Title');
            });
            it('should have updates object empty field', function() {
                expect(blog).to.have.deep.property('syncParams.updates').and
                                            .to.be.an('object').and
                                                .to.be.empty;
            });
            blog.stopPolling();
        });

        describe('fetch', function() {
            // Use Sinon to replace jQuery's ajax method
            // with a spy.
            beforeEach(function() {
                sinon.stub($, 'ajax').yieldsTo('success', {
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
                $.ajax.restore();
            });
            it('blog model should make an ajax call to liveblog.server.rest', function(done) {
                var blog = new Blog({Id: 1});
                window.liveblog = {
                    servers: {
                        rest: '//localhost:8080'
                    }
                };
                blog.stopPolling();
                blog.fetch();
                expect($.ajax.calledOnce).to.be.true;
                expect($.ajax.getCall(0).args[0].url).to.equal('//localhost:8080/resources/LiveDesk/Blog/1');
                //expect($.ajax.getCall(0).args[0].headers).to.have.property('X-Format-DateTime').and.to.equal('yyyy-MM-ddTHH:mm:ss\'Z\'');
                expect(blog.get('Id')).equal(1);
                expect(blog.get('EmbedConfig')).to.have.property('UserComments')
                                        .and.to.equal.true;
                expect(blog.get('EmbedConfig')).to.have.property('FrontendServer')
                                        .and.to.equal('//localhost:8080');
                expect(blog.get('Language')).to.have.property('Code')
                                        .and.to.equal('de');
                done(); // let Mocha know we're done async testing
            });
        });

        describe('poller', function() {
            // Use Sinon to replace jQuery's ajax method
            // with a spy.
            beforeEach(function() {
                sinon.stub($, 'ajax').yieldsTo('success', {
                    Id: 4,
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
                $.ajax.restore();
            });

            it('blog model should make an ajax call to liveblog.server.rest', function(done) {
                var BlogFast = Blog.extend({pollInterval: 100});
                var blog = new BlogFast({Id: 4}),
                    options = {
                        crossDomain: true,
                        data: {
                            some: 'kind',
                            of: 'data'
                        }
                    };
                window.liveblog = {
                    servers: {
                        rest: '//localhost:8080'
                    }
                };
                blog.poller(options);
                expect($.ajax.calledOnce).to.be.true;
                expect($.ajax.getCall(0).args[0].url).to.equal('//localhost:8080/resources/LiveDesk/Blog/4');
                expect($.ajax.getCall(0).args[0].crossDomain).to.be.true;
                expect($.ajax.getCall(0).args[0]).to.not.have.property('data');
                expect(blog.get('Id')).equal(4);
                expect(blog.get('EmbedConfig')).to.have.property('UserComments')
                                        .and.to.equal.true;
                expect(blog.get('EmbedConfig')).to.have.property('FrontendServer')
                                        .and.to.equal('//localhost:8080');
                expect(blog.get('Language')).to.have.property('Code')
                                        .and.to.equal('de');
                setTimeout(function() {
                    expect($.ajax.getCall(0).args[0].url).to.equal('//localhost:8080/resources/LiveDesk/Blog/4');
                    expect($.ajax.getCall(1).args[0].url).to.equal('//localhost:8080/resources/LiveDesk/Blog/4');
                    done(); // let Mocha know we're done async testing

                }, blog.pollInterval);
            });

        });

    });
});
