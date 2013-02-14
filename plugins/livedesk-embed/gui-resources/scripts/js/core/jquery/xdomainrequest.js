define(['jquery'],function( jQuery ) {
var root = this;	
if (root.XDomainRequest) {
  jQuery.ajaxTransport("+*",function( s ) {
	if ( s.crossDomain && s.async ) {
	  if ( s.timeout ) {
		s.xdrTimeout = s.timeout;
		delete s.timeout;
	  }
	  var xdr;
	  return {
		send: function( _, complete ) {
		  function callback( status, statusText, responses, responseHeaders ) {
			xdr.onload = xdr.onerror = xdr.ontimeout = jQuery.noop;
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
		  xdr.onload = function(e1, e2) {
			callback( 200, "OK", { text: xdr.responseText }, "Content-Type: " + xdr.contentType );
		  };
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
			xdr.onerror = jQuery.noop();
			xdr.abort();
		  }
		}
	  };
	}
  });
}
});
