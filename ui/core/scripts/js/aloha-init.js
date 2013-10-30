define(['jquery', 'jqueryui/tabs', 'jqueryui/autocomplete', 'jqueryui/sortable'], 
function($)
{
    window.Aloha = 
    {
        settings: 
        {
            bundles: 
            { 
                oer: config.cjs('aloha-plugins/oer'),
                superdesk: config.cjs('aloha-plugins/superdesk'),
                // TODO these have no place here
                impl: config.content_url + '/' + config.guiJs('superdesk/article', 'aloha')
            },
            predefinedModules: 
            {
                'jquery': $,
                'jqueryui': $.ui
            },
            jQuery: $
        }
    };
    var 
    alohaDfd = new $.Deferred,
    load = function()
    {
        require
        ({ 
            templatePaths:
            {
                'default': config.core('')+'templates/',
                'plugin': config.gui('{plugin}/templates/')
            },
            waitSeconds: 15,
            context: 'aloha', 
            baseUrl: config.cjs('aloha/src/lib'),
            paths:
            {
                // For the repository browser
                'PubSub': 'vendor/pubsub/js/pubsub-unminified',
                'Class': 'vendor/class',
                'RepositoryBrowser': 'vendor/repository-browser/js/repository-browser-unminified',
                'jstree': 'vendor/jquery.jstree',              // Mutates jquery
                'jqgrid': 'vendor/jquery.jqgrid',              // Mutates jquery
                'jquery-layout': 'vendor/jquery.layout-1.3.0-rc30.7',     // Mutates jquery
                'jqgrid-locale-en': 'vendor/grid.locale.en', // Mutates jqgrid
                'jqgrid-locale-de': 'vendor/grid.locale.de', // Mutates jqgrid
                'repository-browser-i18n-de': 'vendor/repository-browser/js/repository-browser-unminified',
                'repository-browser-i18n-en': 'vendor/repository-browser/js/repository-browser-unminified',

                // Shortcuts for all common plugins
                "ui": "../plugins/common/ui/lib",
                "ui/vendor": "../plugins/common/ui/vendor",
                "ui/css": "../plugins/common/ui/css",
                "ui/nls": "../plugins/common/ui/nls",
                "ui/res": "../plugins/common/ui/res",
                "link": "../plugins/common/link/lib",
                "link/vendor": "../plugins/common/link/vendor",
                "link/css": "../plugins/common/link/css",
                "link/nls": "../plugins/common/link/nls",
                "link/res": "../plugins/common/link/res",
                "table": "../plugins/common/table/lib",
                "table/vendor": "../plugins/common/table/vendor",
                "table/css": "../plugins/common/table/css",
                "table/nls": "../plugins/common/table/nls",
                "table/res": "../plugins/common/table/res",
                "list": "../plugins/common/list/lib",
                "list/vendor": "../plugins/common/list/vendor",
                "list/css": "../plugins/common/list/css",
                "list/nls": "../plugins/common/list/nls",
                "list/res": "../plugins/common/list/res",
                "image": "../plugins/common/image/lib",
                "image/vendor": "../plugins/common/image/vendor",
                "image/css": "../plugins/common/image/css",
                "image/nls": "../plugins/common/image/nls",
                "image/res": "../plugins/common/image/res",
                "highlighteditables": "../plugins/common/highlighteditables/lib",
                "highlighteditables/vendor": "../plugins/common/highlighteditables/vendor",
                "highlighteditables/css": "../plugins/common/highlighteditables/css",
                "highlighteditables/nls": "../plugins/common/highlighteditables/nls",
                "highlighteditables/res": "../plugins/common/highlighteditables/res",
                "format": "../plugins/common/format/lib",
                "format/vendor": "../plugins/common/format/vendor",
                "format/css": "../plugins/common/format/css",
                "format/nls": "../plugins/common/format/nls",
                "format/res": "../plugins/common/format/res",
                "dom-to-xhtml": "../plugins/common/dom-to-xhtml/lib",
                "dom-to-xhtml/vendor": "../plugins/common/dom-to-xhtml/vendor",
                "dom-to-xhtml/css": "../plugins/common/dom-to-xhtml/css",
                "dom-to-xhtml/nls": "../plugins/common/dom-to-xhtml/nls",
                "dom-to-xhtml/res": "../plugins/common/dom-to-xhtml/res",
                "contenthandler": "../plugins/common/contenthandler/lib",
                "contenthandler/vendor": "../plugins/common/contenthandler/vendor",
                "contenthandler/css": "../plugins/common/contenthandler/css",
                "contenthandler/nls": "../plugins/common/contenthandler/nls",
                "contenthandler/res": "../plugins/common/contenthandler/res",
                "characterpicker": "../plugins/common/characterpicker/lib",
                "characterpicker/vendor": "../plugins/common/characterpicker/vendor",
                "characterpicker/css": "../plugins/common/characterpicker/css",
                "characterpicker/nls": "../plugins/common/characterpicker/nls",
                "characterpicker/res": "../plugins/common/characterpicker/res",
                "commands": "../plugins/common/commands/lib",
                "commands/vendor": "../plugins/common/commands/vendor",
                "commands/css": "../plugins/common/commands/css",
                "commands/nls": "../plugins/common/commands/nls",
                "commands/res": "../plugins/common/commands/res",
                "align": "../plugins/common/align/lib",
                "align/vendor": "../plugins/common/align/vendor",
                "align/css": "../plugins/common/align/css",
                "align/nls": "../plugins/common/align/nls",
                "align/res": "../plugins/common/align/res",
                "abbr": "../plugins/common/abbr/lib",
                "abbr/vendor": "../plugins/common/abbr/vendor",
                "abbr/css": "../plugins/common/abbr/css",
                "abbr/nls": "../plugins/common/abbr/nls",
                "abbr/res": "../plugins/common/abbr/res",
                "block": "../plugins/common/block/lib",
                "block/vendor": "../plugins/common/block/vendor",
                "block/css": "../plugins/common/block/css",
                "block/nls": "../plugins/common/block/nls",
                "block/res": "../plugins/common/block/res",
                "horizontalruler": "../plugins/common/horizontalruler/lib",
                "horizontalruler/vendor": "../plugins/common/horizontalruler/vendor",
                "horizontalruler/css": "../plugins/common/horizontalruler/css",
                "horizontalruler/nls": "../plugins/common/horizontalruler/nls",
                "horizontalruler/res": "../plugins/common/horizontalruler/res",
                "undo": "../plugins/common/undo/lib",
                "undo/vendor": "../plugins/common/undo/vendor",
                "undo/css": "../plugins/common/undo/css",
                "undo/nls": "../plugins/common/undo/nls",
                "undo/res": "../plugins/common/undo/res",
                "paste": "../plugins/common/paste/lib",
                "paste/vendor": "../plugins/common/paste/vendor",
                "paste/css": "../plugins/common/paste/css",
                "paste/nls": "../plugins/common/paste/nls",
                "paste/res": "../plugins/common/paste/res",

                // Shortcuts for some often used extra plugins (not all)
                "cite": "../plugins/extra/cite/lib",
                "cite/vendor": "../plugins/extra/cite/vendor",
                "cite/css": "../plugins/extra/cite/css",
                "cite/nls": "../plugins/extra/cite/nls",
                "cite/res": "../plugins/extra/cite/res",
                "flag-icons": "../plugins/extra/flag-icons/lib",
                "flag-icons/vendor": "../plugins/extra/flag-icons/vendor",
                "flag-icons/css": "../plugins/extra/flag-icons/css",
                "flag-icons/nls": "../plugins/extra/flag-icons/nls",
                "flag-icons/res": "../plugins/extra/flag-icons/res",
                "numerated-headers": "../plugins/extra/numerated-headers/lib",
                "numerated-headers/vendor": "../plugins/extra/numerated-headers/vendor",
                "numerated-headers/css": "../plugins/extra/numerated-headers/css",
                "numerated-headers/nls": "../plugins/extra/numerated-headers/nls",
                "numerated-headers/res": "../plugins/extra/numerated-headers/res",
                "formatlesspaste": "../plugins/extra/formatlesspaste/lib",
                "formatlesspaste/vendor": "../plugins/extra/formatlesspaste/vendor",
                "formatlesspaste/css": "../plugins/extra/formatlesspaste/css",
                "formatlesspaste/nls": "../plugins/extra/formatlesspaste/nls",
                "formatlesspaste/res": "../plugins/extra/formatlesspaste/res",
                "linkbrowser": "../plugins/extra/linkbrowser/lib",
                "linkbrowser/vendor": "../plugins/extra/linkbrowser/vendor",
                "linkbrowser/css": "../plugins/extra/linkbrowser/css",
                "linkbrowser/nls": "../plugins/extra/linkbrowser/nls",
                "linkbrowser/res": "../plugins/extra/linkbrowser/res",
                "imagebrowser": "../plugins/extra/imagebrowser/lib",
                "imagebrowser/vendor": "../plugins/extra/imagebrowser/vendor",
                "imagebrowser/css": "../plugins/extra/imagebrowser/css",
                "imagebrowser/nls": "../plugins/extra/imagebrowser/nls",
                "imagebrowser/res": "../plugins/extra/imagebrowser/res",
                "ribbon": "../plugins/extra/ribbon/lib",
                "ribbon/vendor": "../plugins/extra/ribbon/vendor",
                "ribbon/css": "../plugins/extra/ribbon/css",
                "ribbon/nls": "../plugins/extra/ribbon/nls",
                "ribbon/res": "../plugins/extra/ribbon/res",
                "toc": "../plugins/extra/toc/lib",
                "toc/vendor": "../plugins/extra/toc/vendor",
                "toc/css": "../plugins/extra/toc/css",
                "toc/nls": "../plugins/extra/toc/nls",
                "toc/res": "../plugins/extra/toc/res",
                "wai-lang": "../plugins/extra/wai-lang/lib",
                "wai-lang/vendor": "../plugins/extra/wai-lang/vendor",
                "wai-lang/css": "../plugins/extra/wai-lang/css",
                "wai-lang/nls": "../plugins/extra/wai-lang/nls",
                "wai-lang/res": "../plugins/extra/wai-lang/res",
                "headerids": "../plugins/extra/headerids/lib",
                "headerids/vendor": "../plugins/extra/headerids/vendor",
                "headerids/css": "../plugins/extra/headerids/css",
                "headerids/nls": "../plugins/extra/headerids/nls",
                "headerids/res": "../plugins/extra/headerids/res",
                "metaview": "../plugins/extra/metaview/lib",
                "metaview/vendor": "../plugins/extra/metaview/vendor",
                "metaview/css": "../plugins/extra/metaview/css",
                "metaview/nls": "../plugins/extra/metaview/nls",
                "metaview/res": "../plugins/extra/metaview/res",
                "listenforcer": "../plugins/extra/listenforcer/lib",
                "listenforcer/vendor": "../plugins/extra/listenforcer/vendor",
                "listenforcer/css": "../plugins/extra/listenforcer/css",
                "listenforcer/nls": "../plugins/extra/listenforcer/nls",
                "listenforcer/res": "../plugins/extra/listenforcer/res",
                
                //
                'utils': config.cjs('utils'),
                'jquery': config.cjs('jquery'),
                'jqueryui': config.cjs('jquery/ui'),
                'bootstrap': config.cjs('jquery/bootstrap'),
                'dust': config.cjs('dust'),
                'gettext': config.cjs('gettext'),
                'order': config.cjs('require/order'),
                'tmpl': config.cjs('require/tmpl'),
                
                "superdesk/fix": config.cjs("aloha-plugins/superdesk/fix/lib"),
                "superdesk/toolbar": config.cjs("aloha-plugins/superdesk/toolbar/lib/toolbar"),
                "superdesk/image": config.cjs("aloha-plugins/superdesk/image/lib/image"),
                "superdesk/image-plugin": config.cjs("aloha-plugins/superdesk/image/lib/image-plugin"),
                // TODO move to specific plugin
                "impl/image": config.guiJs('superdesk/article', 'aloha/image'),
                
                "ui/toolbar": config.cjs("aloha-plugins/superdesk/toolbar/lib/toolbar"),
                "toolbar/vendor": config.cjs("aloha-plugins/oer/toolbar/vendor"),
                "toolbar/css": config.cjs("aloha-plugins/oer/toolbar/css"),
                "toolbar/nls": config.cjs("aloha-plugins/oer/toolbar/nls"),
                "toolbar/res": config.cjs("aloha-plugins/oer/toolbar/res")
            }
        }, ['aloha'], function(){ alohaDfd.resolve(Aloha); });
    };
    
    return function(settings)
    {
        $.extend(true, Aloha.settings, settings); 
        load(); 
        return alohaDfd; 
    };
    
});