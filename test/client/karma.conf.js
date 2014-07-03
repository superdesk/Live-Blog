'use strict';

module.exports = function(config) {
    config.set({

        // base path that will be used to resolve all patterns (eg. files, exclude)
        basePath: '../..',

        // frameworks to use
        // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
        frameworks: ['mocha', 'requirejs', 'sinon-chai'],

        // list of files / patterns to load in the browser
        // test-main.js must be the first one added
        files: [
            'test/client/test-main.js',
            {pattern: 'gui-themes/themes/base/**/*.dust', included: false},
            {pattern: 'gui-resources/scripts/js/**/*.js', included: false},
            {pattern: 'node_modules/lodash/dist/lodash.compat.min.js', included: false},
            {pattern: 'node_modules/backbone/backbone-min.js', included: false},
            {pattern: 'node_modules/backbone.layoutmanager/backbone.layoutmanager.js', included: false},
            {pattern: 'node_modules/dustjs-linkedin/dist/dust-full.min.js', included: false},
            {pattern: 'node_modules/dustjs-helpers/dist/dust-helpers.min.js', included: false},
            {pattern: 'node_modules/jed/jed.js', included: false},
            {pattern: 'node_modules/moment/min/moment.min.js', included: false},
            {pattern: 'bower_components/moment-timezone/builds/moment-timezone-with-data-2010-2020.js', included: false},
            {pattern: 'test/client/**/*.spec.js', included: false}
        ],

        // list of files to exclude
        // Remember to exclude file with require.js config
        exclude: [
            'gui-resources/scripts/js/main.js'
        ],

        // preprocess matching files before serving them to the browser
        // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
        preprocessors: {},

        // test results reporter to use
        // possible values: 'dots', 'progress'
        // available reporters: https://npmjs.org/browse/keyword/karma-reporter
        reporters: ['progress'],

        // options for junit reporter, used by Bamboo
        junitReporter: {
            outputFile: 'client-test-results.xml'
        },

        // web server port
        port: 9876,

        // enable / disable colors in the output (reporters and logs)
        colors: true,

        // level of logging
        // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
        logLevel: config.LOG_INFO,

        // enable / disable watching file and executing tests whenever any file changes
        autoWatch: true,

        // start these browsers
        // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
        browsers: ['Chrome'],

        // Continuous Integration mode
        // if true, Karma captures browsers, runs the tests and exits
        singleRun: false
    });
};
