'use strict';
var dust = require('dustjs-linkedin'),
    lodash    = require('lodash');

// Check the require cache object for the matching pattern,
//    and if modules with the pattern are found undefine them form requirejs.
dust.clearCache = function(pattern) {
    var srex = new RegExp(pattern);
    lodash.each(dust.cache, function(value, name) {
        if (srex.test(name)) {
            delete dust.cache[name];
        }
    });
};

module.exports = dust;
