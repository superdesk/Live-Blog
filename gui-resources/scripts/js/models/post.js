/* jshint maxcomplexity: false */
'use strict';

define([
    'underscore',
    'models/base-model',
    'lib/helpers/trim-tag',
    'lib/gettext'
], function(_, BaseModel, trimTag, gt) {

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

            if (data.Author) {
                if (data.Author.Source.Type.Key === 'smsblog') {
                    // ugly hack is ugly
                    // @TODO remove this when is resolved on rest server.
                    data.item = 'source/sms';
                } else {
                    if (data.Author.Source.IsModifiable ===  'True' ||
                            data.Author.Source.Name === 'internal') {
                        data.item = 'posttype/' + data.Type.Key;
                    } else if (data.Author.Source.Name === 'google'){
                        data.item  = 'source/google/' + data.Meta.type;
                    } else {
                        data.item = 'source/' + data.Author.Source.Name;
                    }
                }
                if ((data.item === 'source/comments') && data.Meta && data.Meta.AuthorName) {
                    data.Meta.AuthorName = gt.sprintf(
                        gt.gettext('%(full_name)s commentator'), {'full_name': data.Meta.AuthorName});
                }
                data.item = data.item.replace('/advertisement', '/infomercial');
            }

            // liveblog can be set into two instances,
            // frontend is the one that servers the embed and backend could be another instance for admin area.
            // but when we server content with images, links and so on we need to give it frontend url.
            if (data.Content && liveblog && liveblog.servers.backend) {
                data.Content = data.Content.replace(liveblog.servers.backend, liveblog.servers.frontend);
            }
            // send servers.frontend to template so some templates can use it
            // ex: quirks mode use avatar image witch needs to have be set fullpath.
            if (liveblog && liveblog.servers.backend) {
                data.servers = data.servers ? data.servers : {};
                data.servers.frontend = liveblog.servers.frontend;
                data.servers.backend = liveblog.servers.backend;
            }

            return data;
        },

        _manageAnnotations: function(apiAnnotation) {
            var annotation = apiAnnotation;
            // an old implementation is using array if it has before and after annotation
            // or a string if it only has before annotation
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

            // annotation now is according to the new api,
            // remove the the trailing br tag.
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
