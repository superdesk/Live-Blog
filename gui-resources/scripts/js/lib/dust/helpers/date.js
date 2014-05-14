'use strict';

define(['dust/core', 'moment', 'lib/gettext'], function(dust, moment, gt) {

    dust.filters['post-date'] = function(string) {
        var date = moment(string);
        return date.format(gt.pgettext('moment', 'post-date'));
    };
    dust.filters['closed-date'] = function(string) {
        var date = moment(string);
        return date.format(gt.pgettext('moment', 'closed-date'));
    };
    return dust;
});
