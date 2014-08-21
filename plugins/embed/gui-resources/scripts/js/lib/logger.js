/* jshint unused:false */
'use strict';

var Log = require('log');

var Logger = module.exports = function Logger(level, stream) {

    // Set default level to info.
    level = level || 'info';

    // For development stream to provided file.
    if (stream && process.env.NODE_ENV === 'development') {
        return new Log(level, stream);
    // For 'production' & 'forever' stream to stdout.
    } else if (process.env.NODE_ENV === 'production' ||
        process.env.NODE_ENV === 'forever') {
        return new Log(level);
    }
    // Default behaviour is stdout.
    return new Log(level);
};
