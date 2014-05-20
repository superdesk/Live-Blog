'use strict';

define(['backbone-custom', 'lib/gettext'], function(Backbone, gt) {

    var buildMap = {};
        // apiUrl = liveblog.frontendServer,
        // langCode = liveblog.language;
    //API
    return {
        pluginBuilder: 'lib/require/i18n-builder',
        load: function(name, req, onLoad, config) {
            // Append '.json' if no filename given:
            if (!liveblog.language) {
                liveblog.language = liveblog.fallback.language;
            }
            var urlPreCached = liveblog.servers.rest + '/content/cache/locale/plugin-' + name + '-' + liveblog.language + '.json',
                urlPre = liveblog.servers.rest + '/resources/Admin/Plugin/' + name + '/JSONLocale/' + liveblog.language,
                urlCached = req.toUrl(urlPreCached),
                url = req.toUrl(urlPre);

            // Use the same options for the internationalization ajax request
            //     url key need to be supplied in options
            //     error key need to be supplied in options
            var options = {
                    url: urlCached,
                    dataType: 'json',
                    //timeout : 2500,
                    cached: true,
                    processTime: 400,
                    tryCount: 0,
                    retryLimit: 2,
                    success: function(data) {
                        if (config.isBuild) {
                            buildMap[name] = data;
                            onLoad(data);
                        } else {
                            gt.loadMessages(data.livedesk_embed);
                            onLoad(data);
                        }
                        onLoad(data);
                    },
                    // provide url and option for the main request
                    // call errorTimout from the error handler to request again ajax if timeout
                    // if is not a timeout status then maybe a redirect issue is in ie or other browser
                    // so in this case call the urlCached of the internationalization
                    error: function(xhr, textStatus, errorThrown) {
                        if (!this.errorTimeout(xhr, textStatus, errorThrown)) {

                            // provide url option in the form of the urlCached
                            // also apply timeout retries for the urlCached
                            options.url = url;
                            options.cached = false;
                            options.error =  this.errorTimeout;
                            Backbone.ajax(options);
                        }
                    },
                    errorTimeout: function(xhr, textStatus, errorThrown) {
                        if (textStatus === 'timeout') {
                            this.tryCount++;
                            if (this.tryCount <= this.retryLimit) {
                                //try again
                                Backbone.ajax(this);
                                return true;
                            }
                            if (console) {
                                console.log('We have tried ' + this.retryLimit + ' times and it is still not working. We give in. Sorry.');
                            }
                            return false;
                        } else if (!this.cached) {
                            // if the request has faild still load requirejs module but with empty data.
                            onLoad({});
                            return true;
                        }
                        return false;
                    }
                };
            Backbone.ajax(options);
        },
        write: function(pluginName, moduleName, write) {
            if (moduleName in buildMap){
                var content = buildMap[moduleName];
                write('define("' + pluginName + '!' + moduleName + '", function(){ return ' + content + ';});\n');
            }
        }

    };
});
