'use strict';

var liveblogBackend = require('./liveblog_backend');
var backendRequestAuth = liveblogBackend.backendRequestAuth;

var utils = require('./utils');
var getIdFromHref = utils.getIdFromHref;

exports.postCreate = postCreate;
exports.postPublish = postPublish;
exports.postCreateAndPublish = postCreateAndPublish;

function postCreate(args, callback) {
    callback = callback || function() {};
    args = args || {};
    var postContent = args.postContent || 'Test post',
        blogId = args.blogId || protractor.getInstance().params.blogId;
    backendRequestAuth({
        method: 'POST',
        uri: '/my/LiveDesk/Blog/' + blogId + '/Post',
        json: {
            'Meta': {},
            'Content': postContent,
            'Type': 'normal',
            'Creator': '1'
        }
    }, function(e, r, j) {
        callback(e, r, j, getIdFromHref(j.href));
    });
}

function postPublish(args, callback) {
    args = args || {};
    callback = callback || function() {};
    var blogId = args.blogId || protractor.getInstance().params.blogId,
        postId = args.postId;
    if (!postId) {
        throw Error('No postId provided');
    }
    backendRequestAuth({
        method: 'POST',
        uri: '/my/LiveDesk/Blog/' + blogId + '/Post/' + postId + '/Publish',
        json: {}
    }, function(e, r, j) {
        callback(e, r, j);
    });
}

function postCreateAndPublish(args, callback) {
    callback = callback || function() {};
    postCreate(
        args,
        function(e, r, j, id) {
            postPublish({
                    postId: id
                },
                function(e2, r2, j2) {
                    callback(e2, r2, j2, id);
                }
            );
        }
    );
}
