define('dust/helpers/i18n',['jquery','dust/dust', 'jquery/i18n', 'jquery/utils'], function ($, dust, I18n) {
function parseAttributeParams(params) {
	if($.isDefined(params.param1) ) {
		for(var i=1,count=params.length+1, aux=[];i<count;i++) {
			if($.isDefined(params['param'+i])) {
				aux[i] = params['param'+i];
			}
		}
		return aux;
	}
	else {
		return params;
	}
}
var helpers = {
  "npgettext": function(){
	msgid = ( params.msgid );
	msgid_plural = ( params.nmsgid );
	n = ( params.count );
	msgctxt = ( params.context );
    if( params && params.msgid ){
		delete params.msgid;
		if(params.length) {
			chunk.write(npgettext(msgctxt, msgid, msgid_plural, n).format(parseAttributeParams(params)));
		}
		else {
			chunk.write(gettext(msgctxt, msgid, msgid_plural, n).toString());
		}
	}
	else {
      if( window.console ){
        window.console.log( "No expression given!" );
      }
    }
    return chunk;	
  },
  "gettext": function( chunk, context, bodies, params ){
	msgid = ( 	params.msgid );	
	// no msgid
    if( params && params.msgid ){
		delete params.msgid;
		if(params.length) {
			chunk.write(gettext(msgid).format(parseAttributeParams(params)));
		}
		else {
			chunk.write(gettext(msgid).toString());
		}
	}
	else {
      if( window.console ){
        window.console.log( "No expression given!" );
      }
    }
    return chunk;
  },
  "ngettext": function( chunk, context, bodies, params ){
	msgid = ( params.msgid );
	nmsgid = ( params.nmsgid );
	count = ( params.count );
	// no msgid
    if( params && params.msgid && params.nmsgid && params.count ){
		delete params.msgid;
		if(params.length) {
			chunk.write(gettext(msgid).format(parseAttributeParams(params)));
		}
		else {
			chunk.write(gettext(msgid).toString());
		}	
  },
};
if($.isDefined(dust.helpers)) {
	$.extend(dust.helpers, helpers);
} else {
	dust.helpers = helpers;
}
});