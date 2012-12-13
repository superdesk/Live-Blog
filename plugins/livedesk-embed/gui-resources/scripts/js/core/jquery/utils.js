define('jquery/utils',['jquery'], function ($) {
$.trimTag = function( tag, myString ) {
	function recursiveTrim( tag, myString) {
		function simpleTrim ( tag, myString ) {
			if ( typeof myString != 'string') {
				myString = '';
			}
			var slen = myString.length;
			var tlen = tag.length;
			if ( myString.indexOf(tag) === 0) {
				myString = myString.substr(tlen, slen);
			}
			var slen = myString.length;
			var minus = slen-tlen;
			if ( myString.substr(slen-tlen, slen) == tag ) {
				myString = myString.substr(0, slen-tlen);
			}
			return myString;
		};
		var newString = myString;
		var i = 0;
		while ( 1 ) {
			i ++;
			newString = simpleTrim( tag, myString);
			if ( newString == myString ) {
				break;
			}
			myString = newString;
			if ( i > 100) {
				//prevent infinite loop at a cost :)
				break;
			}
		}
		return newString;
	}

	if ( typeof tag === 'string') {
		myString = recursiveTrim( tag, myString );
	} else {
		for ( var c = 0; c < tag.length; c ++ ) {
			var myTag = tag[c];
			myString = recursiveTrim ( myTag, myString );
		}
	}
	return myString;
};
$.isString = function( obj ) {
    return obj && typeof(obj) === 'string';
}
$.isObject = function( obj ) {
    return obj && typeof(obj) === 'object';
};
$.isDefined = function( obj ) {
    return obj && typeof(obj) !== 'undefined';
};
$.combineObj = function(keys, values) {
    var object = {};
    if( $.isArray( values ) ) {
		for (i = 0; i < keys.length; i++) {
			object[keys[i]] = values[i];
		}
	}
	if( $.isFunction(values)) {
		for (i = 0; i < keys.length; i++) {
			object[keys[i]] = values;
		}		
	}
    return object;
};
$.arrayValues = function(obj) {
	var arr = [];
	for(i in obj) {
		arr.push(obj[i]);
	}
	return arr;
};
$.mergeObj = function(first, second) {
	if(arguments.length > 2) {
		for(i=2;i<arguments.length;i++) {
			map = arguments[i];
			if( $.isString( map ) )
				map = map.split(",");
			if( $.isArray(map) ) {
				for(k=0;k<map.length;k++)
						first[map[k]]= second[map[k]];
			}
			else if( $.isObject( map ) ) {
				for(k in map) {
					if( $.isFunction( map[k] ) )
						first[k] = map[k](second,k);
					else
						first[k] = second[map[k]];
				}
			}
		}
	} else {
			for(i in 	first)
				first[i] = second[i];
	}
};
$.styledNodeHtml = function(node)
{
    node = $(node);
    if( node.attr('style') && node.attr('style') !== '')
    {
        var wrapper = $('<span/>');
        $('<span style="'+node.attr('style')+'" />').append(node.html()).appendTo(wrapper);
        return wrapper.html();
    }
    return node.html();
};
$.socialShareWindow = function(url, height, width) {
	var options = 'resizable, height=' + height + ', width=' + width;
	var socialShareWindow = window.open( url, '', options);
	socialShareWindow.focus();
	return false;
}
$.extend($.browser, {language: window.navigator.userLanguage || window.navigator.language});
});