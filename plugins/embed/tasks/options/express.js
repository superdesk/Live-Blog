module.exports = {
    options: {
        script: '<%= paths.scripts  %>/server.js'
    },
    dev: {
        options: {
            livereload: true
        }
    },
    prod: {
        options: {
            background: false
        }
    }
};
