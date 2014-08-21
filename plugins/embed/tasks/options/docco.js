module.exports = {
    test: {
        src: ['test/**/*.js'],
        options: {
            output: 'docs/docco/test'
        }
    },
    scripts: {
        src: [
            '<%= paths.scripts %>/**/*.js',
            '!<%= paths.scripts %>/bower_components/**',
            '!<%= paths.scripts %>/build/**'
        ],
        options: {
            output: 'docs/docco/scripts'
        }
    }
};
