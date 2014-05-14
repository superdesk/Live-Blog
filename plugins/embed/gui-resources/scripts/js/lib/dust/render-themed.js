'use strict';
define(['dust/core', 'dust/themed'], function(dust) {
    dust.renderThemed = function(name, context, callback) {
        dust.render(dust.themed(name), context, function(err, out) {
                if (err) {
                    // TODO: What do we want to do with the error?
                    throw err;
                }
                callback(err, out);
            });
    };
});
