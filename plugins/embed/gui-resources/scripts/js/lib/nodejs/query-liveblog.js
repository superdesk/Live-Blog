'use strict';
var qsReg = 'liveblog[\\[\\.]dev[\\]]?(=([^&#]*))?';

var queryLiveblog = function(qs) {
    qs = decodeURIComponent(qs);
    var liveblog = {};
    // parse the current location href
    //     for the query parametes that starts with liveblog.
    //     override those properies over the existing global liveblog obj.
    //     parse only first and second level of the object.
    qs.replace(new RegExp(qsReg.replace('dev[\\]]?', '([^?=&\\.\\]]+)[\\]]?([\\[\\.]([^?=&\\]]+)[\\]\\.]?)?'), 'g'),
        function (match, key, hasSub, subkey, hasEquality, value) {
        value = decodeURIComponent(value);
        if (hasSub) {
            liveblog[key] = liveblog[key] ? liveblog[key] : {};
            liveblog[key][subkey] = hasEquality ? value : true;
        } else {
            liveblog[key] = hasEquality ? value : true;
        }
    });
    return liveblog;
};

module.exports = queryLiveblog;
