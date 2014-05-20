module.exports = {
    options: {
        // When using a jshintrc file the
        // options can't be overwritten at task level
        jshintrc: true,
        ignores: ['<%= paths.nodeModules %>**', '<%= paths.scripts %>bower_components/**', '<%= paths.build %>**']
    },
    source: {
        src: [
            '<%= paths.scripts %>**/*.js',
            '<%= paths.themes %>**/*.js'
        ]
    },
    tests: {
        src: [
            '<%= paths.test %>**/*.js'
        ]
    },
    grunt: {
        src: [
            'Gruntfile.js'
        ]
    },
    all: {
        src: [
            'Gruntfile.js',
            'tasks/**/*.js',
            '<%= paths.scripts %>**/*.js',
            '<%= paths.themes %>**/*.js',
            '<%= paths.test %>**/*.js'
        ]
    }
};
