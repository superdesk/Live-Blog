/*global describe, beforeEach, expect, it, element, by, jasmine */

var gotoUri = require('./helpers/liveblog_frontend').gotoUri;
var uploadFixtures = require('./helpers/liveblog_fixtures').uploadFixtures;
var postCreateAndPublish = require('./helpers/liveblog_posts.js').postCreateAndPublish;

// Protractor Params:
var pp = protractor.getInstance().params;

describe('Embed', function() {
    'use strict';

    describe(' (when have one post)', function() {
        beforeEach(function(done) {
            uploadFixtures('posts', 1, function(e, r, j) {
                gotoUri('/', function() {
                    done();
                });
            });
        });

        it(' is rendered serverside', function() {
            expect(
                element(by.css('div[data-gimme="liveblog-layout"]'))
                .isDisplayed()
            ).toBe(true);
        });

    });

    describe(' (when blank)', function() {
        beforeEach(function(done) {
            uploadFixtures('posts', 0, function(e, r, j) {
                gotoUri('/', function() {
                    done();
                });
            });
        });

        it(' is updates to show just added post', function() {
            postCreateAndPublish({
                postContent: 'test123'
            });
            console.log(
                '[POST] published:' + jasmine.pp(Date())
            );
            browser.wait(function() {
                return browser.isElementPresent(
                    by.cssContainingText(
                        'div.liveblog-content p.post-text',
                        'test123'
                    )
                );
            }, pp.maxTimeout)
            .then(function() {
                console.log(
                    '[POST] displayed:' + jasmine.pp(Date())
                );
            });
            expect(true).toBe(true);
        }, pp.maxTimeout);

    });

});
