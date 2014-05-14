'use strict';

define(['lib/helpers/object-parse'], function(objectParse) {

    function escapeDust(str) {
        return str
                .replace(/\{/g, '{~lb')
                .replace(/\}/g, '{~rb}')
                .replace(/\{~lb/g, '{~lb}')
                .replace(/((^|[^\\])(\\\\)*)"/g, '$1\\"');
    }

    function parseFunction(fnx, string, callback) {
        var fnxed = new RegExp(fnx + '\\((.*?)(\\);)', 'gi'),
            formatx = ').format(';
        return string.replace(fnxed, function(str_fn, inside_fn) {
            var fstr = '', arr, fparams;
            if (inside_fn.indexOf(formatx) > -1) {
                arr = inside_fn.split(formatx);
                inside_fn = arr[0];
                fparams = arr[1].trim();
                if (fparams[0] !== '[' && fparams[0] !== '{') {
                    fparams = '[' + fparams + ']';
                }
                fparams = objectParse(fparams);
                /*jshint forin: false */
                for (var i in fparams) {
                    if (fparams.hasOwnProperty(i)) {
                        if (isNaN(i)) {
                            fstr = fstr + ' ' + i + '="' + fparams[i] + '"';
                        } else {
                            fstr = fstr + ' param' + (parseInt(i, 10) + 1) + '="' + fparams[i] + '"';
                        }
                    }
                }
            }
            return callback(objectParse('[' + inside_fn + ']'), fstr);
        });
    }

    return function (string) {
    /*  string = parseFunction('dcnpgettext', string, function(arr,fstr){
            return '{@i18n domain="'+arr[0]+'" msgctxt="'+arr[1]+'" msgid="'+escapeDust(arr[2])+'" msgid_plural="'+escapeDust(arr[3])+'" n="'+arr[4]+'" category="'+arr[5]+'"'+fstr+'/}';
        });
        string = parseFunction('dnpgettext', string, function(arr,fstr){
            return '{@i18n domain="'+arr[0]+'" msgctxt="'+arr[1]+'" msgid="'+escapeDust(arr[2])+'" msgid_plural="'+escapeDust(arr[3])+'" n="'+arr[4]+'"'+fstr+'/}';
        });
        string = parseFunction('npgettext', string, function(arr,fstr){
            return '{@i18n msgctxt="'+arr[0]+'" msgid="'+escapeDust(arr[1])+'" msgid_plural="'+escapeDust(arr[2])+'" n="'+arr[3]+'"'+fstr+'/}';
        });
        string = parseFunction('dpgettext', string, function(arr,fstr){
            return '{@i18n domain="'+arr[0]+'" msgctxt="'+arr[1]+'" msgid="'+escapeDust(arr[2])+'"'+fstr+'/}';
        });*/
        string = parseFunction('pgettext', string, function(arr, fstr) {
            return '{@i18n msgctxt="' + arr[0] + '" msgid="' + escapeDust(arr[1]) + '"' + fstr + '/}';
        });
    /*  string = parseFunction('dcngettext', string, function(arr,fstr){
            return '{@i18n domain="'+arr[0]+'" msgid="'+escapeDust(arr[1])+'" msgid_plural="'+escapeDust(arr[2])+'" n="'+arr[3]+'" category="'+arr[4]+'"'+fstr+'/}';
        });
        string = parseFunction('dngettext', string, function(arr,fstr){
            return '{@i18n domain="'+arr[0]+'" msgid="'+escapeDust(arr[1])+'" msgid_plural="'+escapeDust(arr[2])+'" n="'+arr[3]+'"'+fstr+'/}';
        });
    */
        string = parseFunction('ngettext', string, function(arr, fstr) {
            return '{@i18n msgid="' + escapeDust(arr[0]) + '" msgid_plural="' + escapeDust(arr[1]) + '" n="' + arr[2] + '"' + fstr + '/}';
        });
    /*  string = parseFunction('dcgettext', string, function(arr,fstr){
            return '{@i18n domain="'+escapeDust(arr[0])+'" msgid="'+escapeDust(arr[1])+'" category="'+arr[2]+'"'+fstr+'/}';
        });
        string = parseFunction('dgettext', string, function(arr,fstr){
            return '{@i18n domain="'+escapeDust(arr[0])+'" msgid="'+escapeDust(arr[1])+'"'+fstr+'/}';
        });*/
        string = parseFunction('gettext', string, function(arr, fstr) {
            return '{@i18n msgid="' + escapeDust(arr[0]) + '"' + fstr + '/}';
        });
        string = parseFunction('_', string, function(arr, fstr) {
            return '{@i18n msgid="' + escapeDust(arr[0]) + '"' + fstr + '/}';
        });
        return string;
    };
});
