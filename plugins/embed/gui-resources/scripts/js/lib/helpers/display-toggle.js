// Toggle display attribute. (we can't use jQuery toggle because it is not supported by Cheerio)
// Specify with showOrHide if the display attribute should be set to
// 'block' or 'none' by providing a true or falsy value respectively
// If no showOrHide param is provided, just toggle the current state.
'use strict';

define(['underscore'], function(_) {
    var displayToggle = function(el, showOrHide) {
        var dspl = '';
        if (_.isUndefined(showOrHide)) {
            dspl = (el.css('display') === 'block') ? 'none' : 'block';
        } else {
            dspl = showOrHide ? 'block' : 'none';
        }
        el.css('display', dspl);
    };
    return displayToggle;
});
