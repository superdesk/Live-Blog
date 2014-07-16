'use strict';
// regex to catch all relevant parts of an url.
//   parameter[1] = protocol if there is one.
//   parameter[2] = hostname.
//   parameter[3] = port if there is one.
var urlRegex = /^(http[s]?:)?\/{2}([0-9.\-A-Za-z]+)(?::(\d+))?/,
    // regex to catch if the urlString has a http(s) or a relative protocol.
    protocolRegex = /^(http[s]?:)?\/{2}/;

// api to parse url
var urlHref = {
    // fix urlString, forceing a relative protocol if the protocol http(s).
    //   a url for browser always need a relative protocol see https bug @LB-1154
    browserUrl: function(urlString) {
        // if there isn't a http(s) or relative protocol add relative as default.
        urlString = protocolRegex.test(urlString) ? urlString : '//' + urlString;
        urlString = urlString.replace(urlRegex, function(all, protocol, hostname, port) {
            return '//' +
                    hostname +
                    (port && (port !== '80' && port !== '443') ? ':' + port : '');
        });
        return urlString;
    },
    // fix urlString, forceing a http: protocol if the protocol is non or a relative protocol.
    //   nodejs requst module needs a protocol http or https to request a url, relative protocols fails.
    serverUrl: function(urlString) {
        // if there isn't a http(s) or relative protocol add relative as default.
        urlString = protocolRegex.test(urlString) ? urlString : '//' + urlString;
        urlString = urlString.replace(urlRegex, function(all, protocol, hostname, port) {
            // if the protocol is relative add a http: default protocol.
            protocol = protocol ? protocol : 'http:';
            return protocol + '//' + hostname +
                    (port && (port !== '80' && port !== '443') ? ':' + port : '');
        });
        return urlString;
    },
    // get a port from a urlString
    getPort: function(urlString) {
        // if there isn't a http(s) or relative protocol add relative as default.
        var newport = '80';
        urlString = protocolRegex.test(urlString) ? urlString : '//' + urlString;
        urlString.replace(urlRegex, function(all, protocol, hostname, port) {
            newport = port ? port : newport;
        });
        return parseInt(newport, 10);
    },
    // replace a port into a urlString
    replacePort: function(urlString, newport) {
        urlString = urlString.replace(urlRegex, function(all, protocol, hostname, port) {
            // if the protocol is relative add a http: default protocol.
            return (protocol ? protocol: '') + '//' + hostname +
                    ((newport !== '80' && newport !== '443') ? ':' + newport : '');
        });
        return urlString;
    }
};

// Export the Url object for **Node.js** if is in nodjs enviroment.
if (typeof module !== 'undefined' && module.exports) {
    module.exports = urlHref;
}
