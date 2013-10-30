define(function() {
    // Reference Javascript Porter Stemmer. This code corresponds to the
    // original
    // 1980 paper available here:
    // http://tartarus.org/martin/PorterStemmer/def.txt
    // The latest version of this code is available at
    // https://github.com/kristopolous/Porter-Stemmer
    //
    // Original comment:
    // Porter stemmer in Javascript. Few comments, but it's easy to follow
    // against the rules in the original
    // paper, in
    //
    // Porter, 1980, An algorithm for suffix stripping, Program, Vol. 14,
    // no. 3, pp 130-137,
    //
    // see also http://www.tartarus.org/~martin/PorterStemmer

    var stemmer = (function() {
        var step2list = {
            "ational" : "ate",
            "tional" : "tion",
            "enci" : "ence",
            "anci" : "ance",
            "izer" : "ize",
            "bli" : "ble",
            "alli" : "al",
            "entli" : "ent",
            "eli" : "e",
            "ousli" : "ous",
            "ization" : "ize",
            "ation" : "ate",
            "ator" : "ate",
            "alism" : "al",
            "iveness" : "ive",
            "fulness" : "ful",
            "ousness" : "ous",
            "aliti" : "al",
            "iviti" : "ive",
            "biliti" : "ble",
            "logi" : "log"
        },

        step3list = {
            "icate" : "ic",
            "ative" : "",
            "alize" : "al",
            "iciti" : "ic",
            "ical" : "ic",
            "ful" : "",
            "ness" : ""
        },

        c = "[^aeiou]", // consonant
        v = "[aeiouy]", // vowel
        C = c + "[^aeiouy]*", // consonant sequence
        V = v + "[aeiou]*", // vowel sequence

        mgr0 = "^(" + C + ")?" + V + C, // [C]VC... is m>0
        meq1 = "^(" + C + ")?" + V + C + "(" + V + ")?$", // [C]VC[V] is m=1
        mgr1 = "^(" + C + ")?" + V + C + V + C, // [C]VCVC... is m>1
        s_v = "^(" + C + ")?" + v; // vowel in stem

        function dummyDebug() {
        }

        function realDebug() {
            console.log(Array.prototype.slice.call(arguments).join(' '));
        }

        return function(w, debug) {
            var stem, suffix, firstch, re, re2, re3, re4, debugFunction, origword = w;

            if (debug) {
                debugFunction = realDebug;
            } else {
                debugFunction = dummyDebug;
            }

            if (w.length < 3) {
                return w;
            }

            firstch = w.substr(0, 1);
            if (firstch == "y") {
                w = firstch.toUpperCase() + w.substr(1);
            }

            // Step 1a
            re = /^(.+?)(ss|i)es$/;
            re2 = /^(.+?)([^s])s$/;

            if (re.test(w)) {
                w = w.replace(re, "$1$2");
                debugFunction('1a', re, w);

            } else if (re2.test(w)) {
                w = w.replace(re2, "$1$2");
                debugFunction('1a', re2, w);
            }

            // Step 1b
            re = /^(.+?)eed$/;
            re2 = /^(.+?)(ed|ing)$/;
            if (re.test(w)) {
                var fp = re.exec(w);
                re = new RegExp(mgr0);
                if (re.test(fp[1])) {
                    re = /.$/;
                    w = w.replace(re, "");
                    debugFunction('1b', re, w);
                }
            } else if (re2.test(w)) {
                var fp = re2.exec(w);
                stem = fp[1];
                re2 = new RegExp(s_v);
                if (re2.test(stem)) {
                    w = stem;
                    debugFunction('1b', re2, w);

                    re2 = /(at|bl|iz)$/;
                    re3 = new RegExp("([^aeiouylsz])\\1$");
                    re4 = new RegExp("^" + C + v + "[^aeiouwxy]$");

                    if (re2.test(w)) {
                        w = w + "e";
                        debugFunction('1b', re2, w);

                    } else if (re3.test(w)) {
                        re = /.$/;
                        w = w.replace(re, "");
                        debugFunction('1b', re3, w);

                    } else if (re4.test(w)) {
                        w = w + "e";
                        debugFunction('1b', re4, w);
                    }
                }
            }

            // Step 1c
            re = new RegExp("^(.*" + v + ".*)y$");
            if (re.test(w)) {
                var fp = re.exec(w);
                stem = fp[1];
                w = stem + "i";
                debugFunction('1c', re, w);
            }

            // Step 2
            re = /^(.+?)(ational|tional|enci|anci|izer|bli|alli|entli|eli|ousli|ization|ation|ator|alism|iveness|fulness|ousness|aliti|iviti|biliti|logi)$/;
            if (re.test(w)) {
                var fp = re.exec(w);
                stem = fp[1];
                suffix = fp[2];
                re = new RegExp(mgr0);
                if (re.test(stem)) {
                    w = stem + step2list[suffix];
                    debugFunction('2', re, w);
                }
            }

            // Step 3
            re = /^(.+?)(icate|ative|alize|iciti|ical|ful|ness)$/;
            if (re.test(w)) {
                var fp = re.exec(w);
                stem = fp[1];
                suffix = fp[2];
                re = new RegExp(mgr0);
                if (re.test(stem)) {
                    w = stem + step3list[suffix];
                    debugFunction('3', re, w);
                }
            }

            // Step 4
            re = /^(.+?)(al|ance|ence|er|ic|able|ible|ant|ement|ment|ent|ou|ism|ate|iti|ous|ive|ize)$/;
            re2 = /^(.+?)(s|t)(ion)$/;
            if (re.test(w)) {
                var fp = re.exec(w);
                stem = fp[1];
                re = new RegExp(mgr1);
                if (re.test(stem)) {
                    w = stem;
                    debugFunction('4', re, w);
                }
            } else if (re2.test(w)) {
                var fp = re2.exec(w);
                stem = fp[1] + fp[2];
                re2 = new RegExp(mgr1);
                if (re2.test(stem)) {
                    w = stem;
                    debugFunction('4', re2, w);
                }
            }

            // Step 5
            re = /^(.+?)e$/;
            if (re.test(w)) {
                var fp = re.exec(w);
                stem = fp[1];
                re = new RegExp(mgr1);
                re2 = new RegExp(meq1);
                re3 = new RegExp("^" + C + v + "[^aeiouwxy]$");
                if (re.test(stem) || (re2.test(stem) && !(re3.test(stem)))) {
                    w = stem;
                    debugFunction('5', re, re2, re3, w);
                }
            }

            re = /ll$/;
            re2 = new RegExp(mgr1);
            if (re.test(w) && re2.test(w)) {
                re = /.$/;
                w = w.replace(re, "");
                debugFunction('5', re, re2, w);
            }

            // and turn initial Y back to y
            if (firstch == "y") {
                w = firstch.toLowerCase() + w.substr(1);
            }

            return w;
        }
    })();

    var pluralize = (function() {
        var ambiguous = [ 'bison', 'bream', 'carp', 'chassis', 'cod', 'corps',
                'debris', 'deer', 'diabetes', 'equipment', 'elk', 'fish',
                'flounder', 'gallows', 'graffiti', 'headquarters', 'herpes',
                'highjinks', 'homework', 'information', 'mackerel', 'mews',
                'money', 'news', 'rice', 'rabies', 'salmon', 'series', 'sheep',
                'shrimp', 'species', 'swine', 'trout', 'tuna', 'whiting',
                'wildebeest' ], irregular = [ {
            "child" : "children"
        }, {
            "man" : "men"
        }, {
            "person" : "people"
        }, {
            "sex" : "sexes"
        }, {
            "ox" : "oxen"
        }, {
            "foot" : "feet"
        }, {
            "tooth" : "teeth"
        }, {
            "goose" : "geese"
        } ], regular = [ {
            "/y$/i" : 'ies'
        }, {
            "/ife$/i" : 'ives'
        }, {
            "/(antenn|formul|nebul|vertebr|vit)a$/i" : '$1ae'
        }, {
            "/(octop|vir|radi|nucle|fung|cact|stimul)us$/i" : '$1i'
        }, {
            "/(buffal|tomat)o$/i" : '$1oes'
        }, {
            "/(sis)$/i" : 'ses'
        }, {
            "/(matr|vert|ind)(ix|ex)$/i" : '$1ices'
        }, {
            "/(x|ch|ss|sh|s|z)$/i" : '$1es'
        }, {
            "/^(?!talis|.*hu)(.*)man$/i" : '$1men'
        }, {
            "/(.*)/i" : '$1s'
        } ], amb = [], irreg = [], test = [];

        for ( var i = 0; i < ambiguous.length; i++) {
            var x = {};
            x[ambiguous[i]] = ambiguous[i];
            amb.push(x);
        }
        for ( var i = 0; i < irregular.length; i++) {
            var x = {};
            x["/^" + irregular[i][0] + "$/"] = irregular[i][1];
            irreg.push(irregular);
        }

        test.concat(amb).concat(irreg).concat(regular);

        return function(noun) {
            for ( var i = 0; i < test.length; i++)
                console.log(noun.match(test[i][0]));
            // this.izeRegExps(token, customForms) || this.izeAbiguous(token) ||
            // this.izeRegulars(token, formSet) || this.izeRegExps(token,
            // formSet.regularForms) ||
            // token
        }

    })();

    return {
        stemmer : stemmer,
        pluralize : pluralize
    };
});
