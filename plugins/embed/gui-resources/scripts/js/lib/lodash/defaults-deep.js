'use strict';

define(['lodash'], function(_) {
    _.defaultsDeep = _.partialRight(_.merge, _.defaults);
    return _;
});
