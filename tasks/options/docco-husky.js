module.exports = {
    test: {
        src: ['test/**/*.js'],
        options: {
            output: 'docs/docco-husky/test'
        }
    },
    scripts: {
        name: 'Liveblog embed working on nodejs',
        src: [
            '<%= paths.scripts %>/**/*.js',
            '!<%= paths.scripts %>/bower_components/**',
            '!<%= paths.scripts %>/build/**'
        ],
        options: {
            output: 'docs/docco-husky/scripts'
        }
    }
};
