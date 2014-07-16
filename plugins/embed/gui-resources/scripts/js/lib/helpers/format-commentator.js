'use strict';

define([
    'underscore',
    'lib/gettext'
], function(_, gt) {
    return function(name) {
        /*!
         * @TODO: remove this line when LB-1013 is done.
         */
        name = name.replace('commentator', '');
        /*!
         * @ENDTODO
         */
        return gt.sprintf(gt.gettext('%(full_name)s commentator'), {'full_name': name});
    };
});
