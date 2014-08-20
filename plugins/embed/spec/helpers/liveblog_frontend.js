'use strict';

/*global protractor, browser */
var _ = require('lodash');

var utils = require('./utils');
var constructUrl = utils.constructUrl;
var constructGetParameters = utils.constructGetParameters;

var pp = protractor.getInstance().params;

exports.getUrl = getUrl;
exports.gotoUri = gotoUri;

function getUrl(uri) {
    return constructUrl(
        pp.baseUrl, uri
    );
}

// go to app's uri
function gotoUri(uri, callback) {
    callback = callback || function() {};
    var result;
    var url = exports.getUrl(uri) +
        constructGetParameters(_.extend(
            {
                'liveblog.id': pp.blogId,
                'liveblog.servers.rest': pp.backendServerHostname
            },
            pp.baseGetParams
    ));
    browser.getCurrentUrl().then(
        function(currentUrl) {
            if (url === currentUrl) {
                console.log('[BROWSER] refresh page');
                result = browser.refresh();
            } else {
                console.log('[BROWSER] open ' + url);
                result = browser.driver.get(url);
            }
            callback(result);
        }
    );
}
