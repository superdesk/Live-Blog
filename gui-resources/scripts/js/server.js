'use strict';
var express       = require('express'),
    path          = require('path'),
    fs            = require('fs'),
    qs            = require('qs'),
    Logger        = require('./lib/logger'),
    urlHref       = require('./lib/nodejs/url-href'),
    grunt         = require('grunt'),
    lodash        = require('lodash'),
    cors          = require('./lib/nodejs/express/cors'),
    queryLiveblog = require('./lib/nodejs/query-liveblog'),
    cp            = require('child_process');

var server = module.exports = express(),
    config = {
        paths: {
            root: '../../../'
        }
    };
config = lodash.merge(grunt.file.readJSON(path.join(__dirname, config.paths.root, 'config.json')), config);
// parse the grunt configuration style to an proper obj.
grunt.initConfig(config);

config = grunt.config.get();
// prase the nodejs property to a url object.
//   so that we can have the port, protocol and hostname for later use.
server.configure(function() {
    server.use(cors);
    if (config.servers.port){

        server.set('port', config.servers.port);
    } else {
        server.set('port', urlHref.getPort(config.servers.nodejs));
    }
    server.use(express['static'](path.join(__dirname, config.paths.scriptsRoot)));
    server.use(express['static'](path.join(__dirname, config.paths.themesRoot)));
    server.use('/scripts/js/node_modules',
                express['static'](path.join(__dirname, config.paths.nodeModules)));
    server.use('/docs',
                express['static'](path.join(__dirname, config.paths.docs)));
});

config.paths.logs = path.join(__dirname, config.paths.logs);

// Create logger for the server
fs.exists(config.paths.logs, function(exists) {
    if (exists) {
        var logFile = fs.createWriteStream(path.join(config.paths.logs, config.logging.nodejs),
                                            {'flags': 'a'});
        GLOBAL.liveblogLogger = new Logger('info', logFile);
    } else {
        console.log(config.paths.log + ' folder missing, to create it run ' +
                        '"grunt create-logs-folder" or "grunt server"');
    }
});

var configLiveblog = function(liveconfig, config) {
    // add loader browserUrl method to server liveblog global object.
    liveconfig.browserUrl = urlHref.browserUrl;
    if (liveconfig.servers.rest) {
        liveconfig.servers.rest = urlHref.serverUrl(liveconfig.servers.rest);

        liveconfig.servers.frontend = liveconfig.servers.frontend ?
            liveconfig.servers.frontend : liveconfig.servers.rest;

        liveconfig.servers.css = liveconfig.servers.css ?
                liveconfig.servers.css : liveconfig.servers.rest;
    }

    liveconfig.servers.frontend = urlHref.serverUrl(
        liveconfig.servers.frontend ?
            liveconfig.servers.frontend :
                (config.servers.proxy ?
                    config.servers.proxy :
                    config.servers.nodejs)
            );

    liveconfig.servers.livereload = urlHref.replacePort(liveconfig.servers.frontend, config.servers.livereload);

    return liveconfig;
};

server.get('/', function(req, res) {

    liveblogLogger.info('server request, query string %s and user-agent %s',
        (req.query ? ': "' + qs.stringify(req.query) + '"' : ' is empty'),
         req.headers['user-agent']);

    // override the default configuration parametners with
    // the GET query given ones if there are any.
    var liveblog = configLiveblog(lodash.merge(
                        lodash.cloneDeep(config.liveblog),
                        queryLiveblog(req.originalUrl)), config);
    if (!liveblog.servers.rest) {
        //if there is a docco-husky index.html and redirect to that.
        if (fs.existsSync(path.join(__dirname, config.paths.doccoHusky, 'index.html'))) {
            res.redirect(config.paths.doccoHusky);
        } else {
            // docco is the fallback we have a index.html for docco in git.
            res.redirect(config.paths.docco);
        }
    } else {
        cp.exec('nodejs ' + path.join(__dirname, 'app.js'), {env: {NODE_ENV: 'production', liveblog: JSON.stringify(liveblog)}}, function(error, stdout, stderr) {
            var out = JSON.parse(stdout);
            res.send(out.code, out.body);
        });
    }
});

module.exports = server.listen(server.get('port'), function() {
    console.log('Express server listening on port ' + server.get('port'));
});
