define('dust/dust-helpers', ['dust/dust', 'jquery', 'utils/twitter', 'jquery/i18n', 'jquery/utils'], function(dust, $, twitter){
var parseAttributeParams = function(chunk, context, bodies, params) {
  if($.isDefined(params.param1) ) {
    var aux = [], index;
    $.each(params, function(key, value){
      if( typeof value === "function" ){
        val = '';
        chunk.tap( function( data ){
          val += data;
          return '';
        } ).render( value, context ).untap();
        value = val;
      }
      index = parseInt(key.slice(5))-1;
      if(isNaN(index) && window.console) {
        window.console.log( "Invalid parameter "+key+" given!" );
        return [];
      }
      aux[index] = value;
    });
		return aux;
	}
	else {
    $.each(params, function(key, value){
      if( typeof value === "function" ){
        val = '';
        chunk.tap( function( data ){
          val += data;
          return '';
        } ).render( value, context ).untap();
        params[key] = val;
      }
    });
		return params;
	}
};

var helpers = { 
  "i18n": function( chunk, context, bodies, params ){
	msgid = ( params.msgid );
	msgid_plural = ( params.msgid_plural );
	n = ( params.n );
	domain = ( params.domain );
	msgctxt = ( params.msgctxt );
    if( params && params.msgid ){
		delete params.msgid;
		chunk.write($.i18n.dcnpgettext(domain, msgctxt, msgid, msgid_plural, n).format(parseAttributeParams(chunk, context, bodies, params)));
	}
	else {
      if( window.console ){
        window.console.log( "No expression given!" );
      }
    }
    return chunk;	
  },  
  sep: function(chunk, context, bodies) {
    if (context.stack.index === context.stack.of - 1) {
      return chunk;
    }
    return bodies.block(chunk, context);
  },

  idx: function(chunk, context, bodies) {
    return bodies.block(chunk, context.push(context.stack.index));
  },
  
  "if": function( chunk, context, bodies, params ){
    var cond = ( params.cond );
    
    if( params && params.cond ){
      // resolve dust references in the expression
      if( typeof cond === "function" ){
        cond = '';
        chunk.tap( function( data ){
          cond += data;
          return '';
        } ).render( params.cond, context ).untap();
        if( cond === '' ){
          cond = false;
        }
      }
      // eval expressions with no dust references
      if( eval( cond ) ){
       return chunk.render( bodies.block, context );
      } 
      if( bodies['else'] ){
       return chunk.render( bodies['else'], context );
      }
    } 
    // no condition
    else {
      if( window.console ){
        window.console.log( "No expression given!" );
      }
    }
    return chunk;
  }
};

dust.helpers = helpers;

dust.filters.t = function(string){ return $('<div>'+string+'</div>').text(); }
dust.filters.twitter_all = function(string) { return twitter.link.all(string); }

function getAnnotation(idx)
{
    return function(content)
    {
        try
        {
            var content = JSON.parse(content);
            return content.annotation[idx];
        }
        catch(e){}
        return '';
    };
}
dust.filters.twitter_annotation_before = getAnnotation(0);
dust.filters.twitter_annotation_after = getAnnotation(1);

return dust;
});