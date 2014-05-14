'use strict';
define(['dust/core', 'lib/helpers/twitter'], function(dust, twitter) {

    dust.filters.twitter_all = function(string) { return twitter.link.all(string); };

    return dust;
});
