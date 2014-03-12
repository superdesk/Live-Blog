var jQuery = window.jQuery,
    oldjQuery = jQuery && !!jQuery.fn.jquery.match(/^1\.[0-7](\.|$)/);
// check for jQuery
if (!jQuery || oldjQuery) {
    var clientJquery = window.jQuery,
        clientDolar = window.$;
    require.config({
        paths: {
            'jquery': 'core/jquery'
        }
    });
    require(['jquery'], function(){
        window.$ = clientDolar;
        window.jQuery = clientJquery;
    });
} else {
    // register the current jQuery
    define('jquery', [], function() { return jQuery; });
}