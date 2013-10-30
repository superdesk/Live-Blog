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

/*
 * Dust-helpers - Additional functionality for dustjs-linkedin package v1.1.1
 * Copyright (c) 2012, LinkedIn
 * Released under the MIT License. 
 */
function isSelect(context) {
    var value = context.current();
    return typeof value === "object" && value.isSelect === true;
  }

  // Utility method : toString() equivalent for functions
  function jsonFilter(key, value) {
    if (typeof value === "function") {
      return value.toString();
    }
    return value;
  }
//Utility method: to invoke the given filter operation such as eq/gt etc
function filter(chunk, context, bodies, params, filterOp) {
  params = params || {};
  var body = bodies.block,
      actualKey,
      expectedValue,
      filterOpType = params.filterOpType || '';
  // when @eq, @lt etc are used as standalone helpers, key is required and hence check for defined
  if ( typeof params.key !== "undefined") {
    actualKey = dust.helpers.tap(params.key, chunk, context);
  }
  else if (isSelect(context)) {
    actualKey = context.current().selectKey;
    // supports only one of the blocks in the select to be selected
    if (context.current().isResolved) {
      filterOp = function() { return false; };
    }
  }
  else {
    _console.log ("No key specified for filter in:" + filterOpType + " helper ");
    return chunk;
  }
  expectedValue = dust.helpers.tap(params.value, chunk, context);
  // coerce both the actualKey and expectedValue to the same type for equality and non-equality compares
  if (filterOp(coerce(expectedValue, params.type, context), coerce(actualKey, params.type, context))) {
    if (isSelect(context)) {
      context.current().isResolved = true;
    }
    // we want helpers without bodies to fail gracefully so check it first
    if(body) {
     return chunk.render(body, context);
    }
    else {
      _console.log( "Missing body block in the " + filterOpType + " helper ");
      return chunk;
    }
   }
   else if (bodies['else']) {
    return chunk.render(bodies['else'], context);
  }
  return chunk;
}
function coerce (value, type, context) {
    if (value) {
      switch (type || typeof(value)) {
        case 'number': return +value;
        case 'string': return String(value);
        case 'boolean': {
          value = (value === 'false' ? false : value);
          return Boolean(value);
        }
        case 'date': return new Date(value);
        case 'context': return context.get(value);
      }
    }

    return value;
  }

/* end LinkedIn code */

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
  },
  /*
   * Dust-helpers - Additional functionality for dustjs-linkedin package v1.1.1
   * Copyright (c) 2012, LinkedIn
   * Released under the MIT License. 
   */
  "select": function(chunk, context, bodies, params) {
      var body = bodies.block;
      // key is required for processing, hence check for defined
      if( params && typeof params.key !== "undefined"){
        // returns given input as output, if the input is not a dust reference, else does a context lookup
        var key = dust.helpers.tap(params.key, chunk, context);
        // bodies['else'] is meaningless and is ignored
        if( body ) {
         return chunk.render(bodies.block, context.push({ isSelect: true, isResolved: false, selectKey: key }));
        }
        else {
         _console.log( "Missing body block in the select helper ");
         return chunk;
        }
      }
      // no key
      else {
        _console.log( "No key given in the select helper!" );
      }
      return chunk;
    },
    "tap": function( input, chunk, context ){
        // return given input if there is no dust reference to resolve
        var output = input;
        // dust compiles a string/reference such as {foo} to function,
        if( typeof input === "function"){
          // just a plain function (a.k.a anonymous functions) in the context, not a dust `body` function created by the dust compiler
          if( input.isFunction === true ){
            output = input();
          } else {
            output = '';
            chunk.tap(function(data){
               output += data;
               return '';
              }).render(input, context).untap();
            if( output === '' ){
              output = false;
            }
          }
        }
       return output;
      },

      /**
    eq helper compares the given key is same as the expected value
    It can be used standalone or in conjunction with select for multiple branching
    @param key, The actual key to be compared ( optional when helper used in conjunction with select)
    either a string literal value or a dust reference
    a string literal value, is enclosed in double quotes, e.g. key="foo"
    a dust reference may or may not be enclosed in double quotes, e.g. key="{val}" and key=val are both valid
    @param value, The expected value to compare to, when helper is used standalone or in conjunction with select
    @param type (optional), supported types are number, boolean, string, date, context, defaults to string
    Note : use type="number" when comparing numeric
    **/
      "eq": function(chunk, context, bodies, params) {
        if(params) {
          params.filterOpType = "eq";
        }
        return filter(chunk, context, bodies, params, function(expected, actual) { return actual === expected; });
      },

      /**
    ne helper compares the given key is not the same as the expected value
    It can be used standalone or in conjunction with select for multiple branching
    @param key, The actual key to be compared ( optional when helper used in conjunction with select)
    either a string literal value or a dust reference
    a string literal value, is enclosed in double quotes, e.g. key="foo"
    a dust reference may or may not be enclosed in double quotes, e.g. key="{val}" and key=val are both valid
    @param value, The expected value to compare to, when helper is used standalone or in conjunction with select
    @param type (optional), supported types are number, boolean, string, date, context, defaults to string
    Note : use type="number" when comparing numeric
    **/
      "ne": function(chunk, context, bodies, params) {
        if(params) {
          params.filterOpType = "ne";
          return filter(chunk, context, bodies, params, function(expected, actual) { return actual !== expected; });
        }
       return chunk;
      },

      /**
    lt helper compares the given key is less than the expected value
    It can be used standalone or in conjunction with select for multiple branching
    @param key, The actual key to be compared ( optional when helper used in conjunction with select)
    either a string literal value or a dust reference
    a string literal value, is enclosed in double quotes, e.g. key="foo"
    a dust reference may or may not be enclosed in double quotes, e.g. key="{val}" and key=val are both valid
    @param value, The expected value to compare to, when helper is used standalone or in conjunction with select
    @param type (optional), supported types are number, boolean, string, date, context, defaults to string
    Note : use type="number" when comparing numeric
    **/
      "lt": function(chunk, context, bodies, params) {
         if(params) {
           params.filterOpType = "lt";
           return filter(chunk, context, bodies, params, function(expected, actual) { return actual < expected; });
         }
      },

      /**
    lte helper compares the given key is less or equal to the expected value
    It can be used standalone or in conjunction with select for multiple branching
    @param key, The actual key to be compared ( optional when helper used in conjunction with select)
    either a string literal value or a dust reference
    a string literal value, is enclosed in double quotes, e.g. key="foo"
    a dust reference may or may not be enclosed in double quotes, e.g. key="{val}" and key=val are both valid
    @param value, The expected value to compare to, when helper is used standalone or in conjunction with select
    @param type (optional), supported types are number, boolean, string, date, context, defaults to string
    Note : use type="number" when comparing numeric
    **/
      "lte": function(chunk, context, bodies, params) {
         if(params) {
           params.filterOpType = "lte";
           return filter(chunk, context, bodies, params, function(expected, actual) { return actual <= expected; });
         }
        return chunk;
      },


      /**
    gt helper compares the given key is greater than the expected value
    It can be used standalone or in conjunction with select for multiple branching
    @param key, The actual key to be compared ( optional when helper used in conjunction with select)
    either a string literal value or a dust reference
    a string literal value, is enclosed in double quotes, e.g. key="foo"
    a dust reference may or may not be enclosed in double quotes, e.g. key="{val}" and key=val are both valid
    @param value, The expected value to compare to, when helper is used standalone or in conjunction with select
    @param type (optional), supported types are number, boolean, string, date, context, defaults to string
    Note : use type="number" when comparing numeric
    **/
      "gt": function(chunk, context, bodies, params) {
        // if no params do no go further
        if(params) {
          params.filterOpType = "gt";
          return filter(chunk, context, bodies, params, function(expected, actual) { return actual > expected; });
        }
        return chunk;
      },

     /**
    gte helper, compares the given key is greater than or equal to the expected value
    It can be used standalone or in conjunction with select for multiple branching
    @param key, The actual key to be compared ( optional when helper used in conjunction with select)
    either a string literal value or a dust reference
    a string literal value, is enclosed in double quotes, e.g. key="foo"
    a dust reference may or may not be enclosed in double quotes, e.g. key="{val}" and key=val are both valid
    @param value, The expected value to compare to, when helper is used standalone or in conjunction with select
    @param type (optional), supported types are number, boolean, string, date, context, defaults to string
    Note : use type="number" when comparing numeric
    **/
      "gte": function(chunk, context, bodies, params) {
         if(params) {
          params.filterOpType = "gte";
          return filter(chunk, context, bodies, params, function(expected, actual) { return actual >= expected; });
         }
        return chunk;
      },

      // to be used in conjunction with the select helper
      // TODO: fix the helper to do nothing when used standalone
      "default": function(chunk, context, bodies, params) {
        // does not require any params
         if(params) {
            params.filterOpType = "default";
          }
         return filter(chunk, context, bodies, params, function(expected, actual) { return true; });
      },

      /**
    * size helper prints the size of the given key
    * Note : size helper is self closing and does not support bodies
    * @param key, the element whose size is returned
    */
      "size": function( chunk, context, bodies, params ) {
        var key, value=0, nr, k;
        params = params || {};
        key = params.key;
        if (!key || key === true) { //undefined, null, "", 0
          value = 0;
        }
        else if(dust.isArray(key)) { //array
          value = key.length;
        }
        else if (!isNaN(parseFloat(key)) && isFinite(key)) { //numeric values
          value = key;
        }
        else if (typeof key === "object") { //object test
          //objects, null and array all have typeof ojbect...
          //null and array are already tested so typeof is sufficient http://jsperf.com/isobject-tests
          nr = 0;
          for(k in key){
            if(Object.hasOwnProperty.call(key,k)){
              nr++;
            }
          }
          value = nr;
        } else {
          value = (key + '').length; //any other value (strings etc.)
        }
        return chunk.write(value);
      }
    /* end LinkedIn code */

};

dust.helpers = helpers;

dust.filters.t = function(string){ return $('<div>'+string+'</div>').text(); }
dust.filters.trim50 = function(string){ return string.trunc(50, true);}
dust.filters.trim150 = function(string){ return string.trunc(150, true);}
dust.filters.trim200 = function(string){ return string.trunc(200, true);}
dust.filters.twitter_all = function(string) { return twitter.link.all(string); }

dust.filters.strps = function(string){ return string.replace(/\s+|\t+|\r+|\n+/g, ''); }

dust.filters.o = function(string){ console.log(string); return ''; }

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
};

dust.filters.twitter_annotation_before = getAnnotation(0);
dust.filters.twitter_annotation_after = getAnnotation(1);

/**
 * Return locale aware date for given utc date
 */
dust.filters.userdate = function(content) {
  var date = new Date(content);
  if (!isNaN(date.getTime())) {
    return date.toLocaleString();
  }

  return content;
};

return dust;
});