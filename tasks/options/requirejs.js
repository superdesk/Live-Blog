module.exports = {
    compile: {
        options: {
            mainConfigFile: '<%= paths.scripts %>/main.js',
            baseUrl: '<%= paths.scripts %>/',
            name: 'main',
            out: '<%= paths.build  %>/app.min.js',
            findNestedDependencies: true
        }
    }
};
