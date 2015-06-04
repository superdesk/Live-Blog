'use strict';

define(['dust/core', 'lib/gettext', 'moment', 'moment-timezone'], function(dust, gt, moment) {

    dust.filters['post-date'] = function(string) {
        var date = moment(string);
        if (gt.pgettext('moment', 'timezone') !== 'timezone') {
            date.tz(gt.pgettext('moment', 'timezone'));
        }
        return date.format(gt.pgettext('moment', 'post-date'));
    };
    dust.filters['splitted-post-time'] = function(string) {
        var date = moment(string);
        if (gt.pgettext('moment', 'timezone') !== 'timezone') {
            date.tz(gt.pgettext('moment', 'timezone'));
        }
        return date.format(gt.pgettext('moment', 'splitted-post-time'));
    };
    dust.filters['splitted-post-date'] = function(string) {
        var date = moment(string);
        if (gt.pgettext('moment', 'timezone') !== 'timezone') {
            date.tz(gt.pgettext('moment', 'timezone'));
        }
        return date.format(gt.pgettext('moment', 'splitted-post-date'));
    };
    dust.filters['closed-date'] = function(string) {
        var date = moment(string);
        if (gt.pgettext('moment', 'timezone') !== 'timezone') {
            date.tz(gt.pgettext('moment', 'timezone'));
        }
        return date.tz('Europe/Berlin').format(gt.pgettext('moment', 'closed-date'));
    };
    return dust;
});
