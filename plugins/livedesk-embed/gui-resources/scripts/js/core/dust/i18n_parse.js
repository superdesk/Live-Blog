define(['utils/json_parse', 'utils/extend'],function(json_parse){
function escape_dust(str){
	return str.replace(/\{/g,'{~lb').replace(/\}/g, '{~rb}').replace(/\{~lb/g,'{~lb}').replace(/((^|[^\\])(\\\\)*)"/g,'$1\\"');
}

function parseFunction(fnx, string, callback) {
	var fnx = new RegExp(fnx+'\\((.*?)(\\);)','gi');
	var formatx = ').format(';
	return string.replace(fnx, function(str_fn, inside_fn){
		fstr = '';
		if(inside_fn.indexOf(formatx)>-1) {
			arr = inside_fn.split(formatx);
			inside_fn = arr[0];
			fparams = arr[1].trim();
			if(fparams[0] !== '[' || fparams[0] !== '{')
				fparams = '['+fparams+']';
			fparams = json_parse(fparams);
			for(i in fparams) {
				if(isNaN(i)) {
					fstr += ' '+i+'="'+fparams[i]+'"';
				} else {
					fstr += ' param'+(parseInt(i)+1)+'="'+fparams[i]+'"';
				}
			}
		}
		return callback(json_parse('['+inside_fn+']'),fstr);
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