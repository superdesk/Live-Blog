module.exports = {
    options: {
        globals: ['expect', '_', 'Backbone', 'sinon', 'liveblog'],
        timeout: 3000,
        ignoreLeaks: false,
        ui: 'bdd',
        reporter: 'dot'
    },
    all: {
        src: [
            '<%= paths.test %>/server/spechelper.js',
            '<%= paths.test %>/server/**/*.spec.js'
        ]
    },
    bamboo: {
        src: '<%= mochaTest.all.src %>',
        options: {
            reporter: 'xunit',
            captureFile: 'server-test-results.xml'
        }
    }
};
