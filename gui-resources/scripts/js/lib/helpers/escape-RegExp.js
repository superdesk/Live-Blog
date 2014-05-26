//escape input to be treated as a literal string within a regular expression
'use strict';

define(function() {
    var escapeRegExp = function(string) {
        return string.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, '\\$1');
    };
    return escapeRegExp;
});
