define(['jquery', 'jquery/i18n', 'jquery/utils', 'jquery/cookie', 'jquery/xdomainrequest'], function($){

	
    var buildMap = {},
	apiUrl = livedesk.FrontendServer,
	langCode = $.cookie('superdesk.langcode');
    if(livedesk.language) {
       langCode = livedesk.language;
    } else 
    if(!langCode) {
		langCode = $.browser.language.substring(0,2);
		$.cookie('superdesk.langcode',langCode);
	}
	//resources/Admin/Plugin/superdesk_country/JSONLocale/ro
	//API
    return {

        load : function(name, req, onLoad, config) {
            // support 
            $.support.cors = true;
            // Append '.json' if no filename given:
            nameCached = apiUrl + '/content/cache/locale/plugin-' + name + '-' + langCode + '.json';
			name = apiUrl + '/resources/Admin/Plugin/' + name + '/JSONLocale/' + langCode;
            var urlCached = req.toUrl(nameCached);//+'&t='+(new Date()).getTime(),
                url = req.toUrl(name);//+'&t='+(new Date()).getTime();
                /*!
                 * Use the same options for the internationalization ajax request
                 *   url key need to be supplied in options
                 *   error key need to be supplied in options
                 */
                options = {
                        dataType: 'json',
                        timeout : 1000,
                        processTime: 300,
                        tryCount : 0,
                        retryLimit : 2,
                        statusCode: {
                            500: function(data) {
                                console.log('Oops! There seems to be a server problem, please try again later.'); 
                            },
                            302: function(data) {
                                console.log('Redirect');
                            }
                        },
                        success: function(data){
                            if (config.isBuild) {
                                buildMap[name] = data;
                                onLoad(data);
                            } else {
                                $.i18n.load(data);
                                onLoad(data);
                            }
                        },
                        errorTimeout : function(xhr, textStatus, errorThrown ) {
                            if (textStatus == 'timeout') {
                                this.tryCount++;
                                if (this.tryCount <= this.retryLimit) {
                                    //try again
                                    $.ajax(this);
                                    return true;
                                }
                                console.log('We have tried ' + this.retryLimit + ' times and it is still not working. We give in. Sorry.');
                                return false;
                            }
                        }
                };
                /*!
                 * provide url and option for the main request
                 * call errorTimout from the error handler to request again ajax if timeout
                 * if is not a timeout status then maybe a redirect issue is in ie or other browser
                 * so in this case call the urlCached of the internationalization
                 */
                options.error = function(xhr, textStatus, errorThrown){ 
                    if(!this.errorTimeout(xhr, textStatus, errorThrown)) {
                        /*!
                         * provide url option in the form of the urlCached
                         * also apply timeout retries for the urlCached 
                         */
                        options.url = url;
                        options.error =  this.errorTimeout;
                        $.ajax(options);
                    }
                }
                options.url = urlCached;
                $.ajax(options);
        },

        //write method based on RequireJS official text plugin by James Burke
        //https://github.com/jrburke/requirejs/blob/master/text.js
        write : function(pluginName, moduleName, write){
            if(moduleName in buildMap){
                var content = buildMap[moduleName];
                write('define("'+ pluginName +'!'+ moduleName +'", function(){ return '+ content +';});\n');
            }
        }

    };
});