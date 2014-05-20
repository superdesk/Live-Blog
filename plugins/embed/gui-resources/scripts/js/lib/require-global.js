'use strict';

define(['underscore'], function(_) {
    return _.isFunction(liveblog.require) ? liveblog.require : require;
});
