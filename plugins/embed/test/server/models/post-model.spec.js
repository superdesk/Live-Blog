/*global describe, it, before, beforeEach, after, afterEach, expect, requirejs, sinon */
/*jshint unused: false, -W030, -W024 */
'use strict';

describe('Model post', function() {
    var _ = require('lodash'),
        Post;

    beforeEach(function(done) {
        requirejs(['models/post'], function(PostClass) {
            Post = PostClass;
            done();
        });
    });

    describe('parse', function() {
        var data = {
                meta: {
                    AuthorName: 'Meta Author',
                    Meta: '{"id": 1, "name": "test name", "url": "here [click](http://www.localhost.com)"}'
                },
                posttype: {
                    Id: 1,
                    AuthorName: 'Posttype Author',
                    Author: {
                        Source: {
                            Name: 'internal',
                            IsModifiable: 'True',
                            Type: {
                                Key: ''
                            }
                        }
                    },
                    Type: {
                        Key: 'advertisement'
                    }
                },
                smsblog: {
                    Author: {
                        Source: {
                            IsModifiable: 'False',
                            Name: 'smsblog',
                            Type: {
                                Key: 'smsblog'
                            }
                        }
                    },
                    Type: {
                        Key: 'smsblog'
                    }
                },
                google: {
                    Meta: '{"type": "news"}',
                    Author: {
                        Source: {
                            IsModifiable: 'False',
                            Name: 'google',
                            Type: {
                                Key: 'xml'
                            }
                        }
                    },
                    Type: {
                        Key: 'normal'
                    }
                },
                comments: {
                    Meta: '{"AuthorName": "Comments Author"}',
                    Author: {
                        Source: {
                            IsModifiable: 'False',
                            Name: 'comments',
                            Type: {
                                Key: 'xml'
                            }
                        }
                    },
                    Type: {
                        Key: 'normal'
                    }
                },
                content: {
                    Content: '<img src="//localhost.backend"/>'
                }
            };

        describe('meta', function() {
            it('should have Meta.url string field', function() {
                var post = new Post();
                var parsed = post.parse(_.clone(data.meta));
                expect(parsed).to.have.deep.property('Meta.url')
                        .and.to.be.an('string')
                        .and.to.be.equal('here [click](//www.localhost.com)');
            });

            it('should have Meta.Creator string field', function() {
                var post = new Post();
                var parsed = post.parse(data.meta);

                expect(parsed).to.have.deep.property('Meta.Creator.Name')
                        .and.to.be.an('string')
                        .and.to.be.equal('Meta Author');
            });
        });

        describe('posttype', function() {

            it('should have item string field', function() {
                var post = new Post();
                var parsed = post.parse(data.posttype);

                expect(parsed).to.have.property('item')
                        .and.to.be.an('string')
                        .and.to.be.equal('posttype/infomercial');
            });
        });

        describe('smsblog', function() {
            it('should have item string field', function() {
                var post = new Post();
                var parsed = post.parse(data.smsblog);

                expect(parsed).to.have.property('item')
                        .and.to.be.an('string')
                        .and.to.be.equal('source/sms');
            });
        });

        describe('google', function() {

            it('should have item string field', function() {
                var post = new Post();
                var parsed = post.parse(data.google);

                expect(parsed).to.have.property('item')
                        .and.to.be.an('string')
                        .and.to.be.equal('source/google/news');
            });
        });

        describe('comments', function() {

            it('should have item string field', function() {
                var post = new Post();
                var parsed = post.parse(_.clone(data.comments));

                expect(parsed).to.have.property('item')
                        .and.to.be.an('string')
                        .and.to.be.equal('source/comments');
            });

            it('should have Meta.AuthorName string field', function() {
                var post = new Post();
                var parsed = post.parse(_.clone(data.comments));

                expect(parsed).to.have.deep.property('Meta.AuthorName')
                        .and.to.be.an('string')
                        .and.to.be.equal('Comments Author commentator');
            });

        });

        describe('content', function() {

            it('should have Content string field', function() {
                GLOBAL.liveblog.servers.frontend = '//localhost.frontend';
                GLOBAL.liveblog.servers.backend = '//localhost.backend';
                var post = new Post();
                var parsed = post.parse(_.clone(data.content));
                expect(parsed).to.have.property('Content')
                    .and.to.be.an('string')
                    .and.to.be.equal('<img src="//localhost.frontend"/>');
            });

            it('should have servers object field', function() {
                GLOBAL.liveblog.servers.frontend = '//localhost.frontend';
                GLOBAL.liveblog.servers.backend = '//localhost.backend';
                var post = new Post();
                var parsed = post.parse(_.clone(data.content));
                expect(parsed).to.have.property('servers')
                    .and.to.be.an('object')
                    .and.to.be.deep.equal({
                        frontend: '//localhost.frontend',
                        backend: '//localhost.backend'
                    });
            });
        });
    });

    describe('_manageAnnotations', function() {
        var annotation = {
                array_before: [
                    'annotation before<br />'
                ],
                array: [
                    'annotation before<br />',
                    'annotation after<br/>'
                ],
                object: {
                    'before': 'annotation before<br/>',
                    'after': 'annotation after<br>'
                },
                string: 'annotation before<br/>'
            };

        describe('array', function() {
            it('should have before string field', function() {
                var post = new Post();
                var parsed = post._manageAnnotations(annotation.array);
                expect(parsed).to.have.property('before')
                                .and.to.be.an('string')
                                .and.to.be.equal('annotation before');
            });
            it('should have after string field', function() {
                var post = new Post();
                var parsed = post._manageAnnotations(annotation.array);
                expect(parsed).to.have.property('after')
                                .and.to.be.an('string')
                                .and.to.be.equal('annotation after');
            });
        });
        describe('array_before', function() {
            it('should have before string field', function() {
                var post = new Post();
                var parsed = post._manageAnnotations(annotation.array_before);

                expect(parsed).to.have.property('before')
                                .and.to.be.an('string')
                                .and.to.be.equal('annotation before');
            });
            it('should have after string field', function() {
                var post = new Post();
                var parsed = post._manageAnnotations(annotation.array_before);

                expect(parsed).to.have.property('after')
                                .and.to.be.an('string')
                                .and.to.be.equal('');
            });
        });
        describe('object', function() {
            it('should have before string field', function() {
                var post = new Post();
                var parsed = post._manageAnnotations(annotation.object);

                expect(parsed).to.have.property('before')
                                .and.to.be.an('string')
                                .and.to.be.equal('annotation before');
            });
            it('should have after string field', function() {
                var post = new Post();
                var parsed = post._manageAnnotations(annotation.object);

                expect(parsed).to.have.property('after')
                                .and.to.be.an('string')
                                .and.to.be.equal('annotation after');
            });
        });
        describe('string', function() {
            it('should have before string field', function() {
                var post = new Post();
                var parsed = post._manageAnnotations(annotation.string);

                expect(parsed).to.have.property('before')
                                .and.to.be.an('string')
                                .and.to.be.equal('annotation before');
            });
            it('should have after string field', function() {
                var post = new Post();
                var parsed = post._manageAnnotations(annotation.string);

                expect(parsed).to.have.property('after')
                                .and.to.be.an('string')
                                .and.to.be.equal('');
            });
        });
    });

});
