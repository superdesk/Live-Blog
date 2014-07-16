/*global requirejs */
'use strict';

var chai      = require('chai'),
    sinonChai = require('sinon-chai');

global.expect    = chai.expect;
global.requirejs = require('requirejs');
global.sinon  = require('sinon');
chai.use(sinonChai);

requirejs.config({
    baseUrl: 'gui-resources/scripts/js',
    //config: {
        //'load-theme': {
            //themesPath: path.join(__dirname, paths.themes) + '/'
        //},
        //'css': {
            //siteRoot: paths.guiThemes
        //}
    //},
    paths: {
        'backbone-custom':      'lib/backbone/backbone-custom',
        layout:                 '../../layout',
        'embed-code':           '../../embed-code',
        dust:                   'lib/dust',
        tmpl:                   'lib/require/tmpl',
        i18n:                   'lib/require/i18n',
        themeBase:              '../../../gui-themes/themes/base',
        'lodash.compat':        '../../../node_modules/lodash/dist/lodash.compat',
        'moment-timezone':      'bower_components/moment-timezone/builds/moment-timezone-with-data-2010-2020',
        'css':                  'lib/require/css'
    },
    map: {
        '*': {
            'underscore': 'lodash.compat',
            'lodash': 'lodash.compat'
        }
    },
    nodeRequire: require
});
