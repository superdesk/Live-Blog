dust.helpers = {
  "sep": function( chunk, context, bodies ){
    if ( context.stack.index === context.stack.of - 1 ){
      return chunk;
    }
    return bodies.block( chunk, context );
  },
  "idx": function( chunk, context, bodies ){
     return bodies.block( chunk, context.push( context.stack.index ) );
  },
  "gettext": function( chunk, context, bodies, params ){
	 return bodies.block( chunk, context.push( context.stack.index ) );
  },
  "if": function( chunk, context, bodies, params ){
    var cond = ( params.cond );
    
    if( params && params.cond ){
      // resolve dust references in the expression
      if( typeof cond === "function" ){
        cond = '';
        boundary = '';
        chunk.tap( function( data ){
          if( boundary !== '' && boundary[boundary.length - 1] === "{" ) {
            data = ( data === '' || data === '}' ) ? false : true;
            boundary = '';
          } else {
            boundary = data;
          }
          cond += data;
          // replace the { } tokens from the  cond value
          cond = cond.replace( "{", "" );
          cond = cond.replace( "}", "" );
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
  },
  
  /**
   * temporary solution for text static i18n strings
   */
  "i18n": function( chunk, context, bodies, params ){
    var i18n_text = params.text;
    if( typeof i18n_text === "function" ) {
      i18n_text = '';
      chunk.tap( function( data ){
          i18n_text += data;
          return '';
      } ).render( params.text, context ).untap();
    } // end if
    return chunk.write( i18n_text ); 
  }
}