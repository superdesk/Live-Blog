'use strict';

/*global protractor */

var request = require('request');
var jsSHA = require('jssha');

var getBackendUrl = require('./liveblog_backend').getBackendUrl;

var pp = protractor.getInstance().params;

exports.getToken = getToken;

// hash token using username and password
function hashToken(username, password, loginToken) {
    var shaPassword = new jsSHA(password, 'ASCII'),
        shaStep1 = new jsSHA(shaPassword.getHash('SHA-512', 'HEX'), 'ASCII'),
        shaStep2 = new jsSHA(loginToken, 'ASCII'),
        HashedToken = shaStep1.getHMAC(username, 'ASCII', 'SHA-512', 'HEX');
    return shaStep2.getHMAC(HashedToken, 'ASCII', 'SHA-512', 'HEX');
}

// acquire auth token using API
function getToken(callback) {
    var username = pp.username,
        password = pp.password;
    request.post({
            url: getBackendUrl('/Security/Authentication'),
            json: {
                'userName': username
            }
        },
        function(error, response, json) {
            var token = json.Token;
            var hashedToken = hashToken(username, password, token);
            request.post({
                url: getBackendUrl('/Security/Authentication/Login'),
                json: {
                    'UserName': username,
                    'Token': token,
                    'HashedToken': hashedToken
                }
            }, function(error, response, json) {
                if (error) {
                    throw new Error(error);
                }
                pp.token = json.Session;
                callback(error, response, json);
            });
        }
    );
}
