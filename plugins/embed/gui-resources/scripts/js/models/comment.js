'use strict';

define([
    'underscore',
    'backbone-custom',
    'models/base-model',
    'collections/posts',
    'lib/utils'
], function(_, Backbone, BaseModel, Posts, utils) {
    return BaseModel.extend({
        setUrlRoot: function(url) {
            this.urlRoot = url;
        }
    });
});
