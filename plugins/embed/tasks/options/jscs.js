module.exports = {
    options: {
        config: '.jscsrc',
        excludeFiles:  ['<%= paths.nodeModules %>**', '<%= paths.scripts %>bower_components/**']
    },
    all: {
        src: ['<%= jshint.all.src %>']
    }
};
