/* jshint maxcomplexity: false */
/* jshint maxstatements: false */
'use strict';

define([
    'underscore',
    'models/base-model',
    'lib/helpers/trim-tag',
    'lib/helpers/format-commentator',
    'lib/helpers/adjust-server-post'
], function(_, BaseModel, trimTag, formatCommentator, adjustServerPost) {

    return BaseModel.extend({

        parse: function(data) {
            if (data.Meta) {
                data.Meta = data.Meta
                            .replace(new RegExp('http://', 'g'), '//')
                            .replace(new RegExp('https://', 'g'), '//');
                data.Meta = JSON.parse(data.Meta);
            } else {
                data.Meta = {};
            }

            if (data.AuthorName) {
                data.Meta.Creator = {'Name': data.AuthorName};
            }

            if (data.Meta.annotation) {
                data.Meta.annotation = this._manageAnnotations(data.Meta.annotation);
            }
            data.item = 'posttype/normal';
            if (_.has(data.Author, 'Source') && _.has(data.Type, 'Key')) {
                data = adjustServerPost(data);
                if (data.Author.Source.IsModifiable ===  'True' ||
                        data.Author.Source.Name === 'internal') {
                    data.item = 'posttype/' + data.Type.Key;
                } else if (data.Author.Source.Name === 'google'){
                    data.item  = 'source/google/' + data.Meta.type;
                } else {
                    data.item = 'source/' + data.Author.Source.Name;
                }
                if (data.item === 'source/comments') {
                    if (_.has(data.Meta, 'AuthorName')) {
                        data.Meta.AuthorName = formatCommentator(data.Meta.AuthorName);
                    }
                    if (_.has(data, 'AuthorName')) {
                        data.AuthorName = formatCommentator(data.AuthorName);
                    }
                }
            }

            // For running Live Blog we can have just one server or two different ones:
            // * frontend: for the embed.
            // * backend: for the admin.
            //
            // When we have content with images or similar and there are two servers,
            // we have to use the frontend one to serve them.
            if (data.Content && liveblog && liveblog.servers.backend) {
                data.Content = data.Content.replace(liveblog.servers.backend, liveblog.servers.frontend);
            }
            // Set `servers.frontend`, needed by some templates.
            // ex: quirks mode avatar image uses fullpath.
            if (liveblog && liveblog.servers.backend) {
                data.servers = data.servers ? data.servers : {};
                data.servers.frontend = liveblog.servers.frontend;
                data.servers.backend = liveblog.servers.backend;
            }

            return data;
        },

        _manageAnnotations: function(apiAnnotation) {
            var annotation = apiAnnotation;
            // An old implementation is using array if it has before and after annotation
            // or a string if it only has before annotation.
            if (_.isArray(apiAnnotation)) {
                annotation = {
                    before: apiAnnotation[0],
                    after: apiAnnotation[1] ? apiAnnotation[1] : ''
                };
            }

            if (_.isString(apiAnnotation)) {
                annotation = {
                    'before': apiAnnotation,
                    'after': ''
                };
            }

            // Annotation according to the new api,
            // remove the trailing `br` tag.
            if (_.isObject(annotation)) {
                annotation = {
                    'before': trimTag(['<br/>', '<br>', '<br />'], annotation.before),
                    'after': trimTag(['<br/>', '<br>', '<br />'], annotation.after)
                };
            }

            return annotation;
        }
    });
});
