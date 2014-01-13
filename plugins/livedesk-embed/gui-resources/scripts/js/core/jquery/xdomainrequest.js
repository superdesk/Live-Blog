define(['jquery'],function( $ ) {

$.support.cors = true;
var root = this,
    /*!
     * Have this incremental time for requests
     * IE is having issues if the onload callback is taking to long to process
     * will fail/abort to call the rest of the request in queue
     */
	count = 0,
	previousTime = 0;
if (root.XDomainRequest) {
  $.ajaxTransport("+*",function( s ) {
	if ( s.crossDomain && s.async ) {
	  if ( s.timeout ) {
		s.xdrTimeout = s.timeout;
		delete s.timeout;
	  }
	  var xdr, processTime;
	  return {
		send: function( _, complete ) {
		  function callback( status, statusText, responses, responseHeaders ) {
			xdr.onload = xdr.onerror = xdr.ontimeout = $.noop;
			xdr = undefined;
			complete( status, statusText, responses, responseHeaders );
		  }
		  xdr = new XDomainRequest();
		  if(s.dataType){
			  var headerThroughUriParameters = "";//header_Accept=" + encodeURIComponent(s.dataType);
			  for(i in s.headers) {
				  headerThroughUriParameters += i +'='+encodeURIComponent(s.headers[i])+'&';
			  }
			  headerThroughUriParameters = headerThroughUriParameters.replace(/(\s+)?.$/, '');
			  s.url = s.url + (s.url.indexOf("?") === -1 ? "?" : "&" ) + headerThroughUriParameters;
		  }
		  xdr.open( s.type, s.url );
		  if(s.processTime) {
		  	processTime = s.processTime;
		  } else {
		  	processTime = (count++)*80;
		  }
		  //console.log(previousTime);
		  xdr.onload = function(e1, e2) {
			setTimeout(function(){ callback( 200, "OK", { text: xdr.responseText }, "Content-Type: " + xdr.contentType ); count = 0;},previousTime);
		  };
		  previousTime = processTime;
		  xdr.onerror = function(e) {
			  //console.error(JSON.stringify(e));
			  callback( 404, "Not Found" );
		  };
		  if ( s.xdrTimeout ) {
			xdr.ontimeout = function() {
			  callback( 0, "timeout" );
			};
			xdr.timeout = s.xdrTimeout;
		  }
		  xdr.send( ( s.hasContent && s.data ) || null );
		},
		abort: function() {
		  if ( xdr ) {
			xdr.onerror = $.noop();
			xdr.abort();
		  }
		}
	  };
	}
  });
}
});
