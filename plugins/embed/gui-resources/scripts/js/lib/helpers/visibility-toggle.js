// Similar to jQuery toggle method but for visibility attribute.
// Specify with showOrHide if the element should be set to
// 'visible' (showOrHide = true) or to 'hidden' (showOrHide = false).
// If no showOrHide param is provided, just toggle the current state.
'use strict';

define(function() {

    var visibilityToggle = function(el, showOrHide) {
        var vsblty = '';
        if (showOrHide !== undefined) {
            vsblty = showOrHide ? 'visible' : 'hidden';
        } else {
            vsblty = (el.css('visibility') === 'visible') ?
                            'hidden' : 'visible';
        }
        el.css('visibility', vsblty);
        return vsblty === 'visible' ? true : false;
    };

    return visibilityToggle;
});
