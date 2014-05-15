'use strict';

define(['dust/core', 'lib/gettext', 'underscore'], function(dust, gt, _) {
    var parseAttributeParams = function(chunk, context, bodies, params) {
        var val = '';
        if (_.has(params, 'param1')) {
            var aux = [], index;
            _.each(params, function(value, key) {
                if (typeof value === 'function'){
                    val = '';
                    chunk.tap(function(data) {
                        val += data;
                        return '';
                    }).render(value, context).untap();
                    value = val;
                }
                index = parseInt(key.slice(5), 10) - 1;
                if (isNaN(index) && console) {
                    console.log('Invalid parameter ' + key + 'given!');
                    return [];
                }
                aux[index] = value;
            });
            return aux;
        } else {
            _.each(params, function(value, key) {
                if (typeof value === 'function'){
                    val = '';
                    chunk.tap(function(data) {
                        val += data;
                        return '';
                    }).render(value, context).untap();
                    params[key] = val;
                }
            });
            return params;
        }
    };

    dust.helpers.i18n = function(chunk, context, bodies, params) {
        if (params && params.msgid){
            var msgid = params.msgid;
            delete params.msgid;
            var text = gt.dcnpgettext(params.domain, params.msgctxt, msgid, params.msgid_plural, params.n);
            chunk.write(gt.sprintf(text, parseAttributeParams(chunk, context, bodies, params)));
        } else {
            if (console){
                console.log('No expression given!');
            }
        }
        return chunk;
    };
    return dust;
});
