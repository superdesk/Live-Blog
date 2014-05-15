'use strict';
var requirejs = require('requirejs'),
    lodash    = require('lodash');
// Set a vector for caching on requirejs object.
requirejs.cache = {};

// This method is triggered by requirejs when a module is added,
//   so we keep all of the module id into the requirejs cache object.
requirejs.onResourceLoad = function (context, map, depArray) {
    requirejs.cache[map.id] = true;
};

// Check the require cache object for the matching pattern,
//    and if modules with the pattern are found undefine them form requirejs.
requirejs.clearCache = function(pattern) {
    var srex = new RegExp(pattern);
    lodash.each(requirejs.cache, function(value, name) {
        if (value && srex.test(name)) {
            requirejs.cache[name] = false;
            requirejs.undef(name);
        }
    });
};

module.exports = requirejs;
