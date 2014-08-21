'use strict';
define(function() {
    return function() {
        /* global RPO */
        if ((typeof(RPO) !== 'undefined') && RPO.reloadIVW) {
            RPO.reloadIVW();
        }
    };
});
