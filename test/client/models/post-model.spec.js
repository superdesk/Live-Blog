// TODO: Set a different jshint config for tests and remove the next lines
/*global describe, it, before, beforeEach, after, afterEach, expect, sinon */
/*jshint unused: false, -W030, -W024 */
'use strict';

define(['models/post'], function(Post) {
    describe('Model post', function() {
        describe('parse', function() {
            var post = new Post(),
                data = {
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
            window.liveblog = {
                servers: {
                    rest: '//localhost:8080',
                    frontend: '//localhost.frontend',
                    backend: '//localhost.backend'
                }
            };

            describe('meta', function() {
                var parsed = post.parse(data.meta);
                it('should have Meta.url string field', function() {
                    expect(parsed).to.have.deep.property('Meta.url')
                            .and.to.be.an('string')
                            .and.to.be.equal('here [click](//www.localhost.com)');
                });

                it('should have Meta.Creator string field', function() {
                    expect(parsed).to.have.deep.property('Meta.Creator.Name')
                            .and.to.be.an('string')
                            .and.to.be.equal('Meta Author');
                });
            });

            describe('posttype', function() {
                var parsed = post.parse(data.posttype);

                it('should have item string field', function() {
                    expect(parsed).to.have.property('item')
                            .and.to.be.an('string')
                            .and.to.be.equal('posttype/infomercial');
                });
            });

            describe('smsblog', function() {
                var parsed = post.parse(data.smsblog);

                it('should have item string field', function() {
                    expect(parsed).to.have.property('item')
                            .and.to.be.an('string')
                            .and.to.be.equal('source/sms');
                });
            });

            describe('google', function() {
                var parsed = post.parse(data.google);

                it('should have item string field', function() {
                    expect(parsed).to.have.property('item')
                            .and.to.be.an('string')
                            .and.to.be.equal('source/google/news');
                });
            });

            describe('comments', function() {
                var parsed = post.parse(data.comments);

                it('should have item string field', function() {
                    expect(parsed).to.have.property('item')
                            .and.to.be.an('string')
                            .and.to.be.equal('source/comments');
                });

                it('should have Meta.AuthorName string field', function() {
                    expect(parsed).to.have.deep.property('Meta.AuthorName')
                            .and.to.be.an('string')
                            .and.to.be.equal('Comments Author commentator');
                });

            });

            describe('content', function() {
                var parsed = post.parse(data.content);

                it('should have Content string field', function() {
                    expect(parsed).to.have.property('Content')
                        .and.to.be.an('string')
                        .and.to.be.equal('<img src="//localhost.frontend"/>');
                });

                it('should have servers object field', function() {
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
            var post = new Post(),
                annotation = {
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
                var parsed = post._manageAnnotations(annotation.array);
                it('should have before string field', function() {
                    expect(parsed).to.have.property('before')
                                    .and.to.be.an('string')
                                    .and.to.be.equal('annotation before');
                });
                it('should have after string field', function() {
                    expect(parsed).to.have.property('after')
                                    .and.to.be.an('string')
                                    .and.to.be.equal('annotation after');
                });
            });
            describe('array_before', function() {
                var parsed = post._manageAnnotations(annotation.array_before);
                it('should have before string field', function() {
                    expect(parsed).to.have.property('before')
                                    .and.to.be.an('string')
                                    .and.to.be.equal('annotation before');
                });
                it('should have after string field', function() {
                    expect(parsed).to.have.property('after')
                                    .and.to.be.an('string')
                                    .and.to.be.equal('');
                });
            });
            describe('object', function() {
                var parsed = post._manageAnnotations(annotation.object);
                it('should have before string field', function() {
                    expect(parsed).to.have.property('before')
                                    .and.to.be.an('string')
                                    .and.to.be.equal('annotation before');
                });
                it('should have after string field', function() {
                    expect(parsed).to.have.property('after')
                                    .and.to.be.an('string')
                                    .and.to.be.equal('annotation after');
                });
            });
            describe('string', function() {
                var parsed = post._manageAnnotations(annotation.string);
                it('should have before string field', function() {
                    expect(parsed).to.have.property('before')
                                    .and.to.be.an('string')
                                    .and.to.be.equal('annotation before');
                });
                it('should have after string field', function() {
                    expect(parsed).to.have.property('after')
                                    .and.to.be.an('string')
                                    .and.to.be.equal('');
                });
            });
        });

    });
});
