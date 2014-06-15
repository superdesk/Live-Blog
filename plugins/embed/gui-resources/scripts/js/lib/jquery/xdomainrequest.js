/* jshint strict: false, forin: false */
/* global XDomainRequest */
define(['jquery'], function($) {
    $.support.cors = true;
    var root = this,
    /*!
     * Have this incremental time for requests
     * IE is having issues if the onload callback is taking to long to process
     * will fail/abort to call the rest of the request in queue
     */
    processing = false,
    previousTime = 30;
    if (root.XDomainRequest) {
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
                            processing = true;
                            xdr.onload = xdr.onerror = xdr.ontimeout = xdr.onprogress = $.noop;
                            xdr = undefined;
                            $.event.trigger('ajaxStop');
                            complete(status, statusText, responses, responseHeaders);
                            processing = false;
                        }
                        xdr = new XDomainRequest();
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
                        if (!s.processTime) {
                            s.processTime = 50;
                        }
                        var timmer = setInterval(function() {
                            if (processing) {
                                return;
                            }
                            clearInterval(timmer);
                            processing = true;
                            setTimeout(function() {
                                xdr.send((s.hasContent && s.data) || null);
                                previousTime = s.processTime;
                            }, previousTime);
                        }, 20);
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
