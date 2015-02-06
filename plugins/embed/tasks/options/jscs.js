module.exports = {
    options: {
        config: '.jscsrc',
        excludeFiles:  ['<%= paths.nodeModules %>**', '<%= paths.scripts %>bower_components/**', '<%= paths.build %>**', '<%= paths.themes %>**/vendor/*.*']
    },
    all: {
        src: ['<%= jshint.all.src %>']
    }
};
