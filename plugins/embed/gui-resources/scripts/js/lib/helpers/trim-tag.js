'use strict';

define([], function() {

    var trimTag = function(tag, myString) {

        var recursiveTrim = function(tag, myString) {
            var simpleTrim = function(tag, myString) {
                if (typeof myString !== 'string') {
                    myString = '';
                }
                var slen = myString.length;
                var tlen = tag.length;
                if (myString.indexOf(tag) === 0) {
                    myString = myString.substr(tlen, slen);
                }
                if (myString.substr(slen - tlen, slen) === tag) {
                    myString = myString.substr(0, slen - tlen);
                }
                return myString;
            };

            var newString = myString;
            var i = 0;
            while (true) {
                i ++;
                newString = simpleTrim(tag, myString);
                if (newString === myString) {
                    break;
                }
                myString = newString;
                if (i > 100) {
                    //prevent infinite loop at a cost :)
                    break;
                }
            }
            return newString;
        };

        if (typeof tag === 'string') {
            myString = recursiveTrim(tag, myString);
        } else {
            for (var c = 0; c < tag.length; c++) {
                var myTag = tag[c];
                myString = recursiveTrim(myTag, myString);
            }
        }
        return myString;
    };

    return trimTag;
});
