'use strict';

module.exports = function(grunt) {

    // Load all grunt task declared in package.json
    require('load-grunt-tasks')(grunt, {scope: ['devDependencies', 'dependencies', 'optionalDependencies']});

    // var server =  grunt.option('server') || 'http://localhost:9000',
    //     port = server.

    // Define basic configuration
    var config;
    try {
        config = grunt.file.readJSON('./config.json');
    } catch (e){
        config = grunt.file.readJSON('./config.sample.json');
    }
    config.pkg = grunt.file.readJSON('./package.json');

    // Load the basic configuration and additional from tasks/options
    require('load-grunt-config')(grunt, {
        config: config,
        configPath: require('path').join(__dirname, 'tasks', 'options'),
        init: true
    });

    // Update the configuration
    grunt.registerTask('update-config', function () {
        // read the sample config
        var configuration = grunt.file.readJSON('./config.sample.json'),
        // load lodash for merging method
            _ = require('lodash');
        // deep extend or aka lodash merge the current config over sample.
        configuration = _.merge(configuration, config);
        // we don't need pkg from the current config.
        delete configuration.pkg;
        // write file with some beautifications.
        grunt.file.write('./config.json', JSON.stringify(configuration, null, 4));
    });

    grunt.registerTask('create-folders', 'Create needed folders', function() {
        grunt.file.mkdir('logs');
    });

    grunt.registerTask('server', 'Start the liveblog embed server', function(target, action, server) {
        // default option configuration.
        grunt.option.init({
            target: 'dev',
            action: 'start',
            server: 'liveblog'
        });
        // get the config always before starting the server
        grunt.task.run('update-config');

        // create needed folders if they don't exist
        grunt.task.run('create-folders');

        // if parametes wherent specified take the ones form options.
        target = target || grunt.option('target');
        action = action || grunt.option('action');
        server = server || grunt.option('server');

        switch (target) {
            case 'dev':
                grunt.task.run(['env:dev', 'express:dev', 'open:dev', 'watch:express']);
                break;
            case 'prod':
                grunt.task.run(['env:prod', 'express:prod']);
                break;
            case 'forever':
                grunt.task.run(['env:forever', 'forever:' + server + ':' + action]);
                break;
        }
    });

    grunt.registerTask('hint', ['jshint:all', 'jscs:all']);
    grunt.registerTask('test', ['karma:once', 'mochaTest:all']);
    grunt.registerTask('build', ['hint', 'less:all', 'requirejs']);
    grunt.registerTask('ci:travis', ['hint', 'karma:travis', 'mochaTest:all', 'coveralls']);
    grunt.registerTask('ci:bamboo', ['karma:bamboo', 'mochaTest:bamboo']);
    grunt.registerTask('default', ['githooks', 'server']);
};
