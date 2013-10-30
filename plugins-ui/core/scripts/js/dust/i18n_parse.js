define(['utils/json_parse', 'utils/extend'],function(json_parse){
/*!
 * function to escape dust elements list left brackets {~lb}
 *    and right brackets {~rb}
 */
function escape_dust(str){
	
	return str.replace(/\{/g,'{~lb').replace(/\}/g, '{~rb}').replace(/\{~lb/g,'{~lb}').replace(/((^|[^\\])(\\\\)*)"/g,'$1\\"');
}

/*!
 * Parser function 
 * require first parameter `fnx` wich should be a string with the name from gettext lib
 *   example: _,gettext, ngettext ...
 * second parameter `string` the dust text to pe parse
 * and last parameter the `replacerFnx` function that is called to replace the i18n gettext string
 *   the replacerFnx should return a dust @i18n helper.
 */
function parseFunction(fnx, string, replacerFnx) {
	/*!
	 * Regular expresion that is used to search for gettext function
	 *   also includs the `fnx` parameter for a better match
	 * for now the gettext function must end with ;
	 */
	var fnx = new RegExp(fnx+'\\((.*?)(\\);)','gi');
	/*!
	 * Format regular expersion that is used when formating the gettext function 
	 *   ex: _('Hello %s').format("World");
	 *       gettext("Good to see you %s with %s").format(["Superdesk", 'Liveblog']);
	 *       ngettext("One new post","%(Count)s new posts", {Count}).format({ "Count": {Count} });
	 * be aware when sending dust parametters like {Count} they should be numbers and when sending
	 *   strings should be like "{Count}" or '{Count}'
	 */
	var formatx = ').format(';
	return string.replace(fnx, function(str_fn, inside_fn){
		fstr = '';
		if(inside_fn.indexOf(formatx)>-1) {
			arr = inside_fn.split(formatx);
			inside_fn = arr[0];
			/*!
			 * Make sure no space was traped.
			 */
			fparams = arr[1].trim();
			/*!
			 * If the arguments in format aren't object or array
			 *   make the arguments an array.
			 */
			if(fparams[0] !== '[' && fparams[0] !== '{')
				fparams = '['+fparams+']';
			/*!
			 * use here a special json_parser function because the parameters
			 *   can be not json default encoded.
			 * ex: { hello: 'World'} if failing JSON.parse
			 */
			fparams = json_parse(fparams);
			/*!
			 * If it is an array then encode dust attributes like
			 *    param1="Superdesk", param2="Liveblog", ...
			 * If an object just use the key like
			 *    hello="World", Count="{Count}", ...
			 */
			for(i in fparams) {
				if(isNaN(i)) {
					fstr += ' '+i+'="'+fparams[i]+'"';
				} else {
					fstr += ' param'+(parseInt(i)+1)+'="'+fparams[i]+'"';
				}
			}
		}
		return replacerFnx(json_parse('['+inside_fn+']'),fstr);
	});
}

function i18n_parse(string) {
/*	string = parseFunction('dcnpgettext', string, function(arr,fstr){
		return '{@i18n domain="'+arr[0]+'" msgctxt="'+arr[1]+'" msgid="'+escape_dust(arr[2])+'" msgid_plural="'+escape_dust(arr[3])+'" n="'+arr[4]+'" category="'+arr[5]+'"'+fstr+'/}';
	});
	string = parseFunction('dnpgettext', string, function(arr,fstr){
		return '{@i18n domain="'+arr[0]+'" msgctxt="'+arr[1]+'" msgid="'+escape_dust(arr[2])+'" msgid_plural="'+escape_dust(arr[3])+'" n="'+arr[4]+'"'+fstr+'/}';
	});
	string = parseFunction('npgettext', string, function(arr,fstr){
		return '{@i18n msgctxt="'+arr[0]+'" msgid="'+escape_dust(arr[1])+'" msgid_plural="'+escape_dust(arr[2])+'" n="'+arr[3]+'"'+fstr+'/}';
	});
	string = parseFunction('dpgettext', string, function(arr,fstr){
		return '{@i18n domain="'+arr[0]+'" msgctxt="'+arr[1]+'" msgid="'+escape_dust(arr[2])+'"'+fstr+'/}';
	});*/
	string = parseFunction('pgettext', string, function(arr,fstr){
		return '{@i18n msgctxt="'+arr[0]+'" msgid="'+escape_dust(arr[1])+'"'+fstr+'/}';
	});
/*	string = parseFunction('dcngettext', string, function(arr,fstr){
		return '{@i18n domain="'+arr[0]+'" msgid="'+escape_dust(arr[1])+'" msgid_plural="'+escape_dust(arr[2])+'" n="'+arr[3]+'" category="'+arr[4]+'"'+fstr+'/}';
	});
	string = parseFunction('dngettext', string, function(arr,fstr){
		return '{@i18n domain="'+arr[0]+'" msgid="'+escape_dust(arr[1])+'" msgid_plural="'+escape_dust(arr[2])+'" n="'+arr[3]+'"'+fstr+'/}';
	});
*/	
	string = parseFunction('ngettext', string, function(arr,fstr){
		return '{@i18n msgid="'+escape_dust(arr[0])+'" msgid_plural="'+escape_dust(arr[1])+'" n="'+arr[2]+'"'+fstr+'/}';
	});
/*	string = parseFunction('dcgettext', string, function(arr,fstr){
		return '{@i18n domain="'+escape_dust(arr[0])+'" msgid="'+escape_dust(arr[1])+'" category="'+arr[2]+'"'+fstr+'/}';
	});
	string = parseFunction('dgettext', string, function(arr,fstr){
		return '{@i18n domain="'+escape_dust(arr[0])+'" msgid="'+escape_dust(arr[1])+'"'+fstr+'/}';
	});*/	
	string = parseFunction('gettext', string, function(arr,fstr){
		return '{@i18n msgid="'+escape_dust(arr[0])+'"'+fstr+'/}';
	});
	string = parseFunction('_', string, function(arr,fstr){
		return '{@i18n msgid="'+escape_dust(arr[0])+'"'+fstr+'/}';
	});
	return string;
}
return i18n_parse;
});