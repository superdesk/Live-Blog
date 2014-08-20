'use strict';

/*global beforeEach, afterEach */

var resetApp = require('./helpers/liveblog_fixtures').resetApp;

// runs before every spec
beforeEach(function(done) {
    // until we start using angular:
    browser.ignoreSynchronization = true;
    resetApp(function() {done();});
});

// runs after every spec
afterEach(function() {});
