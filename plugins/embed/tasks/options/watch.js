module.exports = {
    express: {
        files: ['<%= paths.scripts %>/**/*.js', '<%= paths.themes %>/**/*.js', '<%= paths.themes %>/**/*.dust'],

        tasks: ['express:dev'],
        options: {
            // According to express docu, 'spawn: false' is needed for the
            // server to reload
            livereload: '<%= servers.livereload %>',
            spawn: false
        }
    },
    hint: {
        files: ['<%= jshint.all.src %>'],
        tasks: ['jshint:all', 'jscs:all']
    },
    less: {
        files: ['<%= paths.theme %>/themes/**/*.less'],
        tasks: ['less:all']
    },
    mocha: {
        files: [
            '<%= jshint.source.src %>',
            '<%= jshint.tests.src %>',
            '!<%= paths.test %>/client/**/*.js'
        ],
        tasks: ['mochaTest:all']
    }
};
