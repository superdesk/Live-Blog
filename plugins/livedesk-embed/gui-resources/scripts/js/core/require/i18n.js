define(['jquery', 'jquery/i18n', 'jquery/utils', 'jquery/cookie'], function($){

	
    var buildMap = {},
	apiUrl = config.api_url,
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
            // Append '.json' if no filename given:
			//name = apiUrl + '/content/cache/locale/plugin-' + name + '-' + langCode + '.json';
			name = apiUrl + '/resources/Admin/Plugin/' + name + '/JSONLocale/' + langCode;
			$.ajax({ dataType: 'json', url: req.toUrl(name)}).done(function(data){
				if (config.isBuild) {
                    buildMap[name] = data;
                    onLoad(data);
                } else {
					$.i18n.load(data);
					onLoad(data);
                }
			});
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