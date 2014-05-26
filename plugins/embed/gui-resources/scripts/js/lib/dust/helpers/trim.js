'use strict';
define(['dust/core'], function(dust) {

    var truncateString = function(string, n, useWordBoundary) {
        var tooLong = string.length > n,
            s_ = tooLong ? string.substr(0, n - 1) : string;
        s_ = useWordBoundary && tooLong ? s_.substr(0, s_.lastIndexOf(' ')) : s_;
        return tooLong ? s_ + '...' : s_;
    };

    dust.filters.trim50 = function(string) { return truncateString(string, 50, true); };
    dust.filters.trim150 = function(string) { return truncateString(string, 150, true); };
    dust.filters.trim200 = function(string) { return truncateString(string, 200, true); };
    dust.filters.json = function(obj) {
        return JSON.stringify(obj);
    };
    return dust;
});
