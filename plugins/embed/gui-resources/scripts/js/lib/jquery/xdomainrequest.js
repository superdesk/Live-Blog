/* jshint strict: false, forin: false */
define(['jquery'], function($) {
    $.support.cors = true;
    var root = this;
    if (root.XDomainRequest) {
        // Instantiate a new XDomainRequest so we later use it.
        var xdr = new root.XDomainRequest(),
            // keep the XDomainRequest instances in this process array.
            process = [];
        // In ie7-ie8 prototype.send is an object and can't be called
        //    even if it can be overided
        // keep the oldsend in the instance xdr object of XDomainRequest
        xdr.oldsend = xdr.send;

        // Override the XDomainRequest method send.
        root.XDomainRequest.prototype.send = function() {
            // Keep the `time` on the instance object so later we can garbage collect it.
            this.time = (new Date()).getTime();
            // add the instance obj into the process array.
            process.push(this);
            // request the parent send method.
            xdr.oldsend.apply(this, arguments);
        };
        // Garbage collector for process array.
        // remove every instance object if the time is less then 20 sec ago.
        setInterval(function() {
            var i, now = (new Date()).getTime();
            for (i = 0; i < process.length; i++) {
                if (process[i] && process[i].time + 20000 < now) {
                    process.splice(i, 1);
                }
            }
        }, 20000);
        $.ajaxTransport('+*', function(s) {
            if (s.crossDomain && s.async) {
                if (s.timeout) {
                    s.xdrTimeout = s.timeout;
                    delete s.timeout;
                }
                var xdr;
                return {
                    send: function(_, complete) {
                        function callback(status, statusText, responses, responseHeaders) {
                            xdr.onload = xdr.onerror = xdr.ontimeout = xdr.onprogress = $.noop;
                            $.event.trigger('ajaxStop');
                            complete(status, statusText, responses, responseHeaders);
                        }
                        xdr = new root.XDomainRequest();
                        if (s.dataType){
                            var headerThroughUriParameters = '';//header_Accept=" + encodeURIComponent(s.dataType);
                            for (var i in s.headers) {
                                if (s.headers.hasOwnProperty(i)){
                                    headerThroughUriParameters += i + '=' + encodeURIComponent(s.headers[i]) + '&';
                                }
                            }
                            headerThroughUriParameters = headerThroughUriParameters.replace(/(\s+)?.$/, '');
                            s.url = s.url + (s.url.indexOf('?') === -1 ? '?' : '&') + headerThroughUriParameters;
                        }
                        xdr.open(s.type, s.url);
                        xdr.onload = function(e1, e2) {
                            callback(200, xdr.responseText, {text: xdr.responseText}, 'Content-Type: ' + xdr.contentType);
                        };
                        xdr.onerror = function(e) {
                            callback(500, 'Unable to Process Data');
                        };
                        if (s.xdrTimeout) {
                            xdr.ontimeout = function() {
                                callback(0, 'timeout');
                            };
                            xdr.timeout = s.xdrTimeout;
                        }
                        xdr.send((s.hasContent && s.data) || null);
                    },
                    abort: function() {
                        if (xdr) {
                            xdr.onerror = $.noop();
                            xdr.abort();
                        }
                    }
                };
            }
        });
    }
    return $;
});
