define(function(){
	return {
		encode: function (string) {
			string = string.replace(/\r\n/g, "\n");
			var utftext = "";

			for (var n = 0; n < string.length; n++) {

				var c = string.charCodeAt(n);

				if (c < 128) {
					utftext += String.fromCharCode(c);
				} else if ((c > 127) && (c < 2048)) {
					utftext += String.fromCharCode((c >> 6) | 192);
					utftext += String.fromCharCode((c & 63) | 128);
				} else {
					utftext += String.fromCharCode((c >> 12) | 224);
					utftext += String.fromCharCode(((c >> 6) & 63) | 128);
					utftext += String.fromCharCode((c & 63) | 128);
				}

			}

			return utftext;
		},
		decode: function(string) {
			// http://kevin.vanzonneveld.net
			// +	 original by: Webtoolkit.info (http://www.webtoolkit.info/)
			// +		input by: Aman Gupta
			// +	 improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +	 improved by: Norman "zEh" Fuchs
			// +	 bugfixed by: hitwork
			// +	 bugfixed by: Onno Marsman
			// +		input by: Brett Zamir (http://brett-zamir.me)
			// +	 bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
			// +	 bugfixed by: kirilloid
			// *	   example 1: utf8_decode('Kevin van Zonneveld');
			// *	   returns 1: 'Kevin van Zonneveld'

			var tmp_arr = [],
				i = 0,
				ac = 0,
				c1 = 0,
				c2 = 0,
				c3 = 0,
				c4 = 0;

			string += '';

			while (i < string.length) {
				c1 = string.charCodeAt(i);
				if (c1 <= 191) {
					tmp_arr[ac++] = String.fromCharCode(c1);
					i++;
				} else if (c1 <= 223) {
					c2 = string.charCodeAt(i + 1);
					tmp_arr[ac++] = String.fromCharCode(((c1 & 31) << 6) | (c2 & 63));
					i += 2;
				} else if (c1 <= 239) {
					// http://en.wikipedia.org/wiki/UTF-8#Codepage_layout
					c2 = string.charCodeAt(i + 1);
					c3 = string.charCodeAt(i + 2);
					tmp_arr[ac++] = String.fromCharCode(((c1 & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
					i += 3;
				} else {
					c2 = string.charCodeAt(i + 1);
					c3 = string.charCodeAt(i + 2);
					c4 = string.charCodeAt(i + 3);
					c1 = ((c1 & 7) << 18) | ((c2 & 63) << 12) | ((c3 & 63) << 6) | (c4 & 63);
					c1 -= 0x10000;
					tmp_arr[ac++] = String.fromCharCode(0xD800 | ((c1 >> 10) & 0x3FF));
					tmp_arr[ac++] = String.fromCharCode(0xDC00 | (c1 & 0x3FF));
					i += 4;
				}
			}

			return tmp_arr.join('');
			}
	}
});